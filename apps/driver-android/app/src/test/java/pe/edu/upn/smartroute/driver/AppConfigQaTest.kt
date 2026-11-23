package pe.edu.upn.smartroute.driver

import org.junit.Assert.assertFalse
import org.junit.Assert.assertEquals
import org.junit.Test
import pe.edu.upn.smartroute.driver.di.AppConfig

/** Fail-closed contract: no cross-driver or cross-route mutations from Android QA. */
class AppConfigQaTest {
    private val qaUid = "zMuwbYHLfST2QNdNkfosoCbUZ003"
    private val qaRoute = "fb413b71-c963-570f-be61-500e9eadfb7b"

    @Test fun qa_build_flag_is_the_only_opt_in() {
        assertEquals(BuildConfig.DEBUG && BuildConfig.QA_WRITE_TEST_ENABLED,
            AppConfig.ENABLE_QA_WRITE_TEST)
        assertEquals(BuildConfig.DEBUG && BuildConfig.QA_WRITE_TEST_ENABLED,
            AppConfig.canMutateQaRoute(qaUid, qaRoute))
    }

    @Test fun all_other_identities_and_routes_are_rejected_even_if_opted_in() {
        assertFalse(AppConfig.canMutateQaRoute(null, qaRoute))
        assertFalse(AppConfig.canMutateQaRoute("different-driver", qaRoute))
        assertFalse(AppConfig.canMutateQaRoute(qaUid, "21e3de4b-4002-5870-bc4e-8eafb2826219"))
        assertFalse(AppConfig.canMutateQaRoute(qaUid, "aec305db-6e2f-5923-8b9f-87fcd9b37755"))
        assertFalse(AppConfig.canMutateQaRoute(qaUid, ""))
    }
}
