set -e
cd $HOME/cmp/official/uk-hmrc/opt
V=$(cat ../src/smart-answers/.ruby-version | tr -d ' \n')
MM=${V%.*}
curl -sSfL -o ruby-$V.tar.gz https://cache.ruby-lang.org/pub/ruby/$MM/ruby-$V.tar.gz
tar xzf ruby-$V.tar.gz
cd ruby-$V
./configure --prefix=$HOME/cmp/official/uk-hmrc/opt/ruby --disable-install-doc > ../ruby-configure.log 2>&1
make -j24 > ../ruby-make.log 2>&1
make install > ../ruby-install.log 2>&1
$HOME/cmp/official/uk-hmrc/opt/ruby/bin/ruby -v
echo RUBY_DONE
