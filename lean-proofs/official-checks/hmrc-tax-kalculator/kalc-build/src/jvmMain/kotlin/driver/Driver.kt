package driver

import uk.gov.hmrc.calculator.Calculator
import uk.gov.hmrc.calculator.model.PayPeriod
import uk.gov.hmrc.calculator.model.TaxYear
import uk.gov.hmrc.calculator.model.pension.PensionMethod
import uk.gov.hmrc.calculator.model.CalculatorResponsePayPeriod

// stdin: id;taxCode;scot(0|1);supplied(0|1);wages;period;pensionAge(0|1);pensionMethod(-|PERCENTAGE|MONTHLY_AMOUNT_IN_POUNDS);pensionAmt;year
// stdout: one JSON object per line.
fun pp(r: CalculatorResponsePayPeriod): String =
    "{\"taxRaw\":${r.taxToPayForPayPeriod},\"tax\":${r.taxToPay},\"capped\":${r.maxTaxAmountExceeded}," +
    "\"ee\":${r.employeesNI},\"er\":${r.employersNI},\"takeHome\":${r.takeHome},\"taxFree\":${r.taxFree}," +
    "\"taxable\":${r.taxableIncome},\"taper\":${r.taperingAmountDeduction},\"pension\":${r.pensionContribution}," +
    "\"kAdj\":${r.kCodeAdjustment},\"wages\":${r.wages},\"bands\":[" +
    (r.taxBreakdown ?: emptyList()).joinToString(",") { "[${it.percentage},${it.amount}]" } + "]}"

fun main() {
    val out = System.out.bufferedWriter()
    generateSequence(::readLine).filter { it.isNotBlank() }.forEach { line ->
        val f = line.split(";")
        val res = try {
            val pension = if (f[7] == "-") null else Calculator.PensionContribution(PensionMethod.valueOf(f[7]), f[8].toDouble())
            val c = Calculator(
                taxCode = f[1], userPaysScottishTax = f[2] == "1", userSuppliedTaxCode = f[3] == "1",
                wages = f[4].toDouble(), payPeriod = PayPeriod.valueOf(f[5]), isPensionAge = f[6] == "1",
                taxYear = TaxYear.fromInt(f[9].toInt()), pensionContribution = pension,
            )
            val r = c.run()
            "{\"id\":\"${f[0]}\",\"ok\":true,\"country\":\"${r.country}\",\"isK\":${r.isKCode}," +
                "\"yearly\":${pp(r.yearly)},\"monthly\":${pp(r.monthly)},\"weekly\":${pp(r.weekly)},\"fourWeekly\":${pp(r.fourWeekly)}," +
                "\"clar\":[" + r.listOfClarification.joinToString(",") { "\"" + it.name + "\"" } + "]}"
        } catch (e: Exception) {
            "{\"id\":\"${f[0]}\",\"ok\":false,\"error\":\"${e::class.simpleName}: ${e.message?.replace("\"", "'")}\"}"
        }
        out.write(res); out.newLine()
    }
    out.flush()
}
