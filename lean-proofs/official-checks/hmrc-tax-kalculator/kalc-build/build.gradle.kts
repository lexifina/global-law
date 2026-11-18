// Minimal JVM-only build of hmrc/tax-kalculator 2.16.1 sources (copied verbatim from ../src/tax-kalculator/src).
// The upstream build needs a private GitHub Packages plugin (uk.gov.hmrc.gradle:spotless, formatting only) and iOS
// targets; neither affects the calculation code. Same Kotlin (1.9.24) and library versions as upstream buildSrc.
plugins { kotlin("multiplatform").version("1.9.24") }
repositories { mavenCentral() }
kotlin {
    jvm()
    sourceSets.all { languageSettings.optIn("kotlin.Experimental") }
    sourceSets {
        commonMain.dependencies {
            implementation("com.soywiz.korlibs.klock:klock:2.4.13")
            implementation("co.touchlab:kermit:2.0.4")
        }
        commonTest.dependencies {
            implementation(kotlin("test-common"))
            implementation(kotlin("test-annotations-common"))
            implementation("io.kotlintest:kotlintest-runner-junit5:3.4.2")
            runtimeOnly("org.junit.jupiter:junit-jupiter-engine:5.10.3")
        }
        jvmTest.dependencies {
            implementation(kotlin("test"))
            implementation(kotlin("test-junit5"))
            implementation("org.junit.jupiter:junit-jupiter-params:5.10.3")
        }
    }
}
tasks.named<Test>("jvmTest") { useJUnitPlatform() }
tasks.register("printRuntimeCp") {
    dependsOn("jvmJar")
    doLast {
        val c = kotlin.jvm().compilations.getByName("main")
        println("CP=" + (c.runtimeDependencyFiles!!.files + tasks.named<Jar>("jvmJar").get().archiveFile.get().asFile).joinToString(":"))
    }
}
