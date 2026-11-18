export JAVA_HOME=$HOME/cmp/official/uk-hmrc/opt/jdk17
export PATH=$JAVA_HOME/bin:$PATH
export GRADLE_USER_HOME=$HOME/cmp/official/uk-hmrc/opt/gradle-home
cd $HOME/cmp/official/uk-hmrc/kalc-build
$HOME/cmp/official/uk-hmrc/src/tax-kalculator/gradlew -p . --no-daemon jvmTest printRuntimeCp 2>&1
echo BUILD_EXIT=$?
