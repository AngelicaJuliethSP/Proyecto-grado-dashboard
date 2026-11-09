"""Fixtures XML de ejemplo para las pruebas del parser.

Reproducen los formatos reales de Surefire:
- testng-results.xml (TestNG): totales como atributos del raíz, duration-ms
  por <suite>, test-method con is-config, classname en el <class> padre.
- TEST-*.xml estilo JUnit: atributos del raíz <testsuite>, hijos
  <failure>/<error>/<skipped> por <testcase>.
"""
import textwrap

TESTNG_XML = textwrap.dedent("""\
    <?xml version="1.0" encoding="UTF-8"?>
    <testng-results skipped="0" failed="1" total="3" passed="2">
      <suite name="Suite" duration-ms="12345">
        <test name="Tests">
          <class name="tests.LoginTest">
            <test-method status="PASS" name="successfulLogin" is-config="false"
                         duration-ms="2000" started-at="2026-11-09T15:47:00Z"
                         description="login exitoso">
            </test-method>
            <test-method status="FAIL" name="failedLogin" is-config="false"
                         duration-ms="300" started-at="2026-11-09T15:47:03Z">
              <exception class="java.lang.AssertionError">
                <message>Texto no visible expected [true] but found [false]</message>
              </exception>
            </test-method>
            <test-method status="SKIP" name="skippedTest" is-config="false"
                         duration-ms="0" started-at="2026-11-09T15:47:04Z">
            </test-method>
            <!-- configuraciones: no deben contarse como tests -->
            <test-method status="PASS" name="setUp" is-config="true" duration-ms="100"></test-method>
            <test-method status="PASS" name="tearDown" is-config="true" duration-ms="100"></test-method>
          </class>
        </test>
      </suite>
    </testng-results>
    """)

# XML estilo JUnit con un <failure> SIN hijos (el bug original: un Element
# vacío evalúa False y el fallo se perdía con `find(...) or find(...)`).
JUNIT_FAILURE_XML = textwrap.dedent("""\
    <?xml version="1.0" encoding="UTF-8"?>
    <testsuite name="tests.NavigationTest" time="1.954"
               tests="1" errors="0" skipped="0" failures="1">
      <testcase name="navigateThroughBottomMenu" classname="tests.NavigationTest" time="1.954">
        <failure message="Texto WebdriverIO no visible expected [true] but found [false]"
                 type="java.lang.AssertionError"></failure>
      </testcase>
    </testsuite>
    """)

JUNIT_PASSED_XML = textwrap.dedent("""\
    <?xml version="1.0" encoding="UTF-8"?>
    <testsuite name="tests.LoginTest" time="2.5" tests="1" errors="0" skipped="0" failures="0">
      <testcase name="successfulLogin" classname="tests.LoginTest" time="2.5"/>
    </testsuite>
    """)

JUNIT_SKIPPED_XML = textwrap.dedent("""\
    <?xml version="1.0" encoding="UTF-8"?>
    <testsuite name="tests.SwipeTest" time="0.5" tests="1" errors="0" skipped="1" failures="0">
      <testcase name="swipeCardsAndFindHiddenText" classname="tests.SwipeTest" time="0.0">
        <skipped message="no llego a ejecutarse"></skipped>
      </testcase>
    </testsuite>
    """)

# XML estilo JUnit donde el raíz declara tests=2 pero solo hay 1 testcase:
# el parser debe contar los testcase reales, no confiar en el atributo.
JUNIT_MISMATCH_XML = textwrap.dedent("""\
    <?xml version="1.0" encoding="UTF-8"?>
    <testsuite name="tests.Mixed" time="3.0" tests="2" errors="0" skipped="0" failures="1">
      <testcase name="okTest" classname="tests.Mixed" time="1.0"></testcase>
      <testcase name="brokenTest" classname="tests.Mixed" time="2.0">
        <failure message="boom" type="java.lang.AssertionError"></failure>
      </testcase>
    </testsuite>
    """)
