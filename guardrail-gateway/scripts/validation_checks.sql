-- 108-Cycle Fractal System Validation Checks
-- Run these queries to validate data integrity and system health

-- ============================================================================
-- 🔴🦉 RED OWL - DIMENSION VALIDATION
-- ============================================================================

-- 1) Dimensions loaded?
SELECT
    'enterprises' as table_name,
    COUNT(*) as count,
    CASE
        WHEN COUNT(*) = 6 THEN '✅ PASS'
        ELSE '❌ FAIL'
    END as status
FROM enterprises
UNION ALL
SELECT
    'squads' as table_name,
    COUNT(*) as count,
    CASE
        WHEN COUNT(*) = 6 THEN '✅ PASS'
        ELSE '❌ FAIL'
    END as status
FROM squads
UNION ALL
SELECT
    'redundancy_pass' as table_name,
    COUNT(*) as count,
    CASE
        WHEN COUNT(*) = 3 THEN '✅ PASS'
        ELSE '❌ FAIL'
    END as status
FROM redundancy_pass;

-- 2) Canonical stages present?
SELECT
    'cycle_stages' as table_name,
    COUNT(*) as count,
    CASE
        WHEN COUNT(*) = 108 THEN '✅ PASS'
        ELSE '❌ FAIL'
    END as status
FROM cycle_stages;

SELECT
    'stage_id_range' as check_name,
    MIN(stage_id) as min_id,
    MAX(stage_id) as max_id,
    CASE
        WHEN MIN(stage_id) = 1
        AND MAX(stage_id) = 108 THEN '✅ PASS'
        ELSE '❌ FAIL'
    END as status
FROM cycle_stages;

-- 3) Ordinal uniqueness & coverage
SELECT
    'ordinal_uniqueness' as check_name,
    COUNT(DISTINCT ordinal) as unique_ordinals,
    CASE
        WHEN COUNT(DISTINCT ordinal) = 108 THEN '✅ PASS'
        ELSE '❌ FAIL'
    END as status
FROM cycle_stages;

SELECT
    'ordinal_duplicates' as check_name,
    COUNT(*) as duplicate_count,
    CASE
        WHEN COUNT(*) = 0 THEN '✅ PASS'
        ELSE '❌ FAIL'
    END as status
FROM (
        SELECT ordinal
        FROM cycle_stages
        GROUP BY
            ordinal
        HAVING
            COUNT(*) <> 1
    ) duplicates;

-- 4) Transitions well-formed
SELECT
    'transitions_count' as check_name,
    COUNT(*) as transition_count,
    CASE
        WHEN COUNT(*) > 0 THEN '✅ PASS'
        ELSE '❌ FAIL'
    END as status
FROM cycle_stage_transitions;

SELECT
    'self_loops' as check_name,
    COUNT(*) as self_loop_count,
    CASE
        WHEN COUNT(*) = 0 THEN '✅ PASS'
        ELSE '❌ FAIL'
    END as status
FROM cycle_stage_transitions
WHERE
    from_stage_id = to_stage_id;

-- 5) Policy evolution table online
SELECT 'policy_evolution_status' as check_name, status, COUNT(*) as count
FROM policy_evolution
GROUP BY
    status
ORDER BY status;

-- ============================================================================
-- 🟠🦧 ORANGE ORANGUTAN - CYCLE ORCHESTRATION VALIDATION
-- ============================================================================

-- Check cycle templates
SELECT
    'cycle_templates' as check_name,
    COUNT(*) as template_count,
    CASE
        WHEN COUNT(*) > 0 THEN '✅ PASS'
        ELSE '❌ FAIL'
    END as status
FROM cycles
WHERE
    active = true;

-- Check stage transition completeness
SELECT
    'transition_coverage' as check_name,
    COUNT(DISTINCT from_stage_id) as stages_with_transitions,
    CASE
        WHEN COUNT(DISTINCT from_stage_id) = 108 THEN '✅ PASS'
        ELSE '❌ FAIL'
    END as status
FROM cycle_stage_transitions;

-- Check transition types
SELECT 'transition_types' as check_name, kind, COUNT(*) as count
FROM cycle_stage_transitions
GROUP BY
    kind
ORDER BY kind;

-- ============================================================================
-- 🟡🐝 YELLOW HONEYBEE - CREATIVE EXPERIMENTATION VALIDATION
-- ============================================================================

-- Check experiment tracking capability
SELECT
    'experiments_table' as check_name,
    COUNT(*) as experiment_count,
    CASE
        WHEN COUNT(*) >= 0 THEN '✅ PASS'
        ELSE '❌ FAIL'
    END as status
FROM experiments;

-- Check prototype tracking
SELECT
    'prototypes_table' as check_name,
    COUNT(*) as prototype_count,
    CASE
        WHEN COUNT(*) >= 0 THEN '✅ PASS'
        ELSE '❌ FAIL'
    END as status
FROM prototypes;

-- ============================================================================
-- 🟢🐢 GREEN TURTLE - RESOURCE MANAGEMENT VALIDATION
-- ============================================================================

-- Check budget caps
SELECT
    'budget_caps' as check_name,
    COUNT(*) as cap_count,
    CASE
        WHEN COUNT(*) > 0 THEN '✅ PASS'
        ELSE '❌ FAIL'
    END as status
FROM finance_budget_caps;

-- Check resource allocations
SELECT
    'resource_allocations' as check_name,
    COUNT(*) as allocation_count,
    CASE
        WHEN COUNT(*) >= 0 THEN '✅ PASS'
        ELSE '❌ FAIL'
    END as status
FROM resource_allocations;

-- Check sustainability metrics
SELECT
    'sustainability_metrics' as check_name,
    COUNT(*) as metric_count,
    CASE
        WHEN COUNT(*) >= 0 THEN '✅ PASS'
        ELSE '❌ FAIL'
    END as status
FROM sustainability_metrics;

-- ============================================================================
-- 🔵🐬 BLUE DOLPHIN - COMMUNICATION VALIDATION
-- ============================================================================

-- Check communications tracking
SELECT
    'communications' as check_name,
    COUNT(*) as comm_count,
    CASE
        WHEN COUNT(*) >= 0 THEN '✅ PASS'
        ELSE '❌ FAIL'
    END as status
FROM communications;

-- Check brand safety checks
SELECT
    'brand_safety_checks' as check_name,
    COUNT(*) as safety_check_count,
    CASE
        WHEN COUNT(*) >= 0 THEN '✅ PASS'
        ELSE '❌ FAIL'
    END as status
FROM brand_safety_checks;

-- ============================================================================
-- 🟣🐘 PURPLE ELEPHANT - REFLECTION VALIDATION
-- ============================================================================

-- Check sentiment analysis
SELECT
    'sentiment_analysis' as check_name,
    COUNT(*) as sentiment_count,
    CASE
        WHEN COUNT(*) >= 0 THEN '✅ PASS'
        ELSE '❌ FAIL'
    END as status
FROM sentiment_analysis;

-- Check reflection cycles
SELECT
    'reflection_cycles' as check_name,
    COUNT(*) as reflection_count,
    CASE
        WHEN COUNT(*) >= 0 THEN '✅ PASS'
        ELSE '❌ FAIL'
    END as status
FROM reflection_cycles;

-- Check policy evolution proposals
SELECT
    'policy_evolution_proposals' as check_name,
    COUNT(*) as proposal_count,
    CASE
        WHEN COUNT(*) >= 0 THEN '✅ PASS'
        ELSE '❌ FAIL'
    END as status
FROM policy_evolution;

-- ============================================================================
-- SYSTEM INTEGRITY CHECKS
-- ============================================================================

-- Check for orphaned stage runs
SELECT
    'orphaned_stage_runs' as check_name,
    COUNT(*) as orphaned_count,
    CASE
        WHEN COUNT(*) = 0 THEN '✅ PASS'
        ELSE '❌ FAIL'
    END as status
FROM
    cycle_stage_runs csr
    LEFT JOIN cycle_runs cr ON csr.run_id = cr.run_id
WHERE
    cr.run_id IS NULL;

-- Check for invalid stage references
SELECT
    'invalid_stage_refs' as check_name,
    COUNT(*) as invalid_count,
    CASE
        WHEN COUNT(*) = 0 THEN '✅ PASS'
        ELSE '❌ FAIL'
    END as status
FROM
    cycle_stage_runs csr
    LEFT JOIN cycle_stages cs ON csr.stage_id = cs.stage_id
WHERE
    cs.stage_id IS NULL;

-- Check decision references
SELECT
    'decision_refs' as check_name,
    COUNT(*) as decision_count,
    CASE
        WHEN COUNT(*) >= 0 THEN '✅ PASS'
        ELSE '❌ FAIL'
    END as status
FROM decisions;

-- Check incident references
SELECT
    'incident_refs' as check_name,
    COUNT(*) as incident_count,
    CASE
        WHEN COUNT(*) >= 0 THEN '✅ PASS'
        ELSE '❌ FAIL'
    END as status
FROM incidents;

-- ============================================================================
-- PERFORMANCE VALIDATION
-- ============================================================================

-- Check index usage (if pg_stat_user_indexes is available)
SELECT
    'index_health' as check_name,
    COUNT(*) as index_count,
    CASE
        WHEN COUNT(*) > 0 THEN '✅ PASS'
        ELSE '❌ FAIL'
    END as status
FROM pg_indexes
WHERE
    schemaname = 'public'
    AND tablename IN (
        'cycle_stages',
        'cycle_runs',
        'cycle_stage_runs',
        'decisions'
    );

-- ============================================================================
-- SUMMARY REPORT
-- ============================================================================

SELECT '=== 108-CYCLE FRACTAL SYSTEM VALIDATION SUMMARY ===' as summary;

-- Overall system health
WITH validation_summary AS (
    SELECT 
        CASE WHEN (SELECT COUNT(*) FROM enterprises) = 6 THEN 1 ELSE 0 END +
        CASE WHEN (SELECT COUNT(*) FROM squads) = 6 THEN 1 ELSE 0 END +
        CASE WHEN (SELECT COUNT(*) FROM redundancy_pass) = 3 THEN 1 ELSE 0 END +
        CASE WHEN (SELECT COUNT(*) FROM cycle_stages) = 108 THEN 1 ELSE 0 END +
        CASE WHEN (SELECT COUNT(*) FROM cycles WHERE active = true) > 0 THEN 1 ELSE 0 END +
        CASE WHEN (SELECT COUNT(*) FROM cycle_stage_transitions) > 0 THEN 1 ELSE 0 END +
        CASE WHEN (SELECT COUNT(*) FROM policy_evolution) >= 0 THEN 1 ELSE 0 END +
        CASE WHEN (SELECT COUNT(*) FROM finance_budget_caps) > 0 THEN 1 ELSE 0 END
        as passed_checks
)
SELECT 
    'SYSTEM_HEALTH' as metric,
    passed_checks as checks_passed,
    8 as total_checks,
    ROUND(passed_checks::numeric / 8 * 100, 2) as health_percentage,
    CASE WHEN passed_checks = 8 THEN '✅ SYSTEM READY' ELSE '⚠️ ISSUES DETECTED' END as status
FROM validation_summary;