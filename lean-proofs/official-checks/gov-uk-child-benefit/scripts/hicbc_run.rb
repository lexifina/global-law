# Runs GOV.UK's real ChildBenefitTaxCalculator class (alphagov/smart-answers, file
# lib/smart_answer/calculators/child_benefit_tax_calculator.rb, loaded unmodified) outside Rails.
# Shims: Rails.root, HashWithIndifferentAccess / Hash#with_indifferent_access, and YAML.load_file (this Ruby was
# built without libyaml; the rates file is flat: "YYYY": then "  key: value" lines with dates and numbers).
# Inputs are passed as BigDecimal, which is what SmartAnswer::Money holds (Money#to_f delegates to it).
# stdin: id;tax_year;children;income;allowable_deductions;other_deductions[;part_year_count;start1,end1|start2,end2]
# stdout: id;benefits_claimed_amount;percent_tax_charge;tax_estimate;calculate_adjusted_net_income
require "bigdecimal"
require "date"
require "pathname"
SA = ARGV[0]
module Rails; def self.root; Pathname.new(SA); end; end
class HashWithIndifferentAccess < Hash
  def [](k) = super(k.is_a?(Symbol) ? k.to_s : k)
  def []=(k, v) ; super(k.is_a?(Symbol) ? k.to_s : k, v) ; end
  def merge!(h) ; h.each { |k, v| self[k] = v } ; self ; end
end
class Hash
  def with_indifferent_access
    h = HashWithIndifferentAccess.new
    each { |k, v| h[k.to_s] = v.is_a?(Hash) ? v.with_indifferent_access : v }
    h
  end
end
module YAML
  def self.load_file(path, **_opts)
    out = {}; cur = nil
    File.readlines(path.to_s).each do |l|
      next if l.strip.empty? || l.strip.start_with?("#") || l.start_with?("---")
      if l =~ /\A"?(\w+)"?:\s*\z/ then cur = out[$1] = {}
      elsif l =~ /\A\s+(\w+):\s*(.+?)\s*\z/
        v = $2
        cur[$1] = if v =~ /\A\d{4}-\d\d-\d\d\z/ then Date.parse(v)
                  elsif v =~ /\A[\d_]+\z/ then v.delete("_").to_i
                  elsif v =~ /\A[\d_]*\.\d+\z/ then v.delete("_").to_f
                  else v end
      else raise "unparsed: #{l}" end
    end
    out
  end
end
module SmartAnswer; module Calculators; end; end
load File.join(SA, "lib/smart_answer/calculators/child_benefit_tax_calculator.rb")
C = SmartAnswer::Calculators::ChildBenefitTaxCalculator
STDIN.each_line do |line|
  f = line.strip.split(";")
  next if f.empty?
  c = C.new(children_count: f[2].to_i, tax_year: f[1], income_details: BigDecimal(f[3]),
            allowable_deductions: BigDecimal(f[4]), other_allowable_deductions: BigDecimal(f[5]),
            part_year_children_count: (f[6] || "0").to_i)
  if f[7]
    f[7].split("|").each_with_index do |se, i|
      s, e = se.split(",")
      c.child_number = i + 1
      c.store_date(:start_date, Date.parse(s))
      c.store_date(:end_date, Date.parse(e)) if e && !e.empty?
    end
  end
  puts [f[0], c.benefits_claimed_amount.round(10), c.percent_tax_charge, c.tax_estimate, c.calculate_adjusted_net_income].join(";")
end
