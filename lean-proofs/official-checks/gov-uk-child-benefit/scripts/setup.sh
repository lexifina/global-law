set -x
cd ~/cmp/official/uk-hmrc
git clone --depth 1 --branch 2.16.1 https://github.com/hmrc/tax-kalculator src/tax-kalculator
git -C src/tax-kalculator rev-parse HEAD
git clone --depth 1 https://github.com/alphagov/smart-answers src/smart-answers
git -C src/smart-answers rev-parse HEAD
cd opt
curl -sSL -o jdk.tgz "https://api.adoptium.net/v3/binary/latest/17/ga/linux/x64/jdk/hotspot/normal/eclipse"
curl -sSL -o jdk.sha "https://api.adoptium.net/v3/assets/latest/17/hotspot?os=linux&architecture=x64&image_type=jdk"
mkdir -p jdk17 && tar xzf jdk.tgz -C jdk17 --strip-components 1
jdk17/bin/java -version
python3 -m venv venv && venv/bin/pip -q install pillow
echo SETUP_DONE
