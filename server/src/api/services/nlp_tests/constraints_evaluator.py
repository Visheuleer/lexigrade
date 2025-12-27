def evaluate_hard_constraints(results: dict) -> dict:
    total = len(results)
    failed_tests = {
        test_name: {
            "status": result.get("status"),
            "details": result.get("details", {})
        }
        for test_name, result in results.items()
        if result.get("status") != "pass"
    }

    passed = {
        test_name: {
            "status": result.get("status"),
            "details": result.get("details", {})
        }
        for test_name, result in results.items()
        if result.get("status") == "pass"
    }
    accepted = len(failed_tests) == 0

    return {
        "accepted": accepted,
        "passed_tests": list(passed.keys()),
        "failed_tests": failed_tests,
        "total_tests": total
    }


def evaluate_soft_constraints(
    results: dict,
    min_pass_ratio: float = 0.6
) -> dict:
    total = len(results)

    passed = {
        name: result
        for name, result in results.items()
        if result.get("status") == "pass"
    }

    failed = {
        name: {
            "status": result.get("status"),
            "details": result.get("details", {})
        }
        for name, result in results.items()
        if result.get("status") != "pass"
    }

    pass_ratio = len(passed) / total if total > 0 else 1.0
    accepted = pass_ratio >= min_pass_ratio

    return {
        "accepted": accepted,
        "pass_ratio": pass_ratio,
        "passed_tests": list(passed.keys()),
        "failed_tests": failed,
        "total_tests": total,
        "min_required": min_pass_ratio
    }
