package pe.edu.upn.smartroute.driver

import org.junit.Assert.assertFalse
import org.junit.Assert.assertEquals
import org.junit.Test
import pe.edu.upn.smartroute.driver.di.AppConfig

/** QA writes are debug-only and user-scoped; backend enforces route ownership and QA route guard. */
class AppConfigQaTest {
    private val qaUid = "zMuwbYHLfST2QNdNkfosoCbUZ003"
    private val qaRoute = "fb413b71-c963-570f-be61-500e9eadfb7b"

    @Test fun debug_build_allows_exact_qa_user_without_extra_gradle_flag() {
        assertEquals(BuildConfig.DEBUG && BuildConfig.QA_WRITE_TEST_ENABLED,
            AppConfig.ENABLE_QA_WRITE_TEST)
        assertEquals(BuildConfig.DEBUG && BuildConfig.QA_WRITE_TEST_ENABLED,
            AppConfig.canMutateQaRoute(qaUid, qaRoute))
    }

    @Test fun QA_denial_reason_does_not_expose_firebase_uid() {
        val reason = AppConfig.qaWriteBlockReason("other-test-uid", qaRoute)
        org.junit.Assert.assertNotNull(reason)
        org.junit.Assert.assertFalse(reason!!.contains("other-test-uid"))
        assertEquals(null, AppConfig.qaWriteBlockReason(qaUid, "other-route"))
        org.junit.Assert.assertNotNull(AppConfig.qaWriteBlockReason(null, qaRoute))
    }

    @Test fun other_users_are_rejected_and_route_must_be_present() {
        assertFalse(AppConfig.canMutateQaRoute(null, qaRoute))
        assertFalse(AppConfig.canMutateQaRoute("different-driver", qaRoute))
        assertEquals(BuildConfig.DEBUG && BuildConfig.QA_WRITE_TEST_ENABLED,
            AppConfig.canMutateQaRoute(qaUid, "21e3de4b-4002-5870-bc4e-8eafb2826219"))
        assertEquals(BuildConfig.DEBUG && BuildConfig.QA_WRITE_TEST_ENABLED,
            AppConfig.canMutateQaRoute(qaUid, "aec305db-6e2f-5923-8b9f-87fcd9b37755"))
        assertFalse(AppConfig.canMutateQaRoute(qaUid, ""))
    }
}
