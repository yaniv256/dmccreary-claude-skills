import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SKILL = ROOT / "skills" / "microsim-generator"
GUIDE = SKILL / "references" / "docker-python-lab-guide.md"
RUNTIME = SKILL / "assets" / "docker-python-lab" / "docker-lab.js"
ROUTING = SKILL / "references" / "routing-criteria.md"
ACTIVE_SKILL = SKILL / "SKILL.md"


class DockerPythonLabContractTests(unittest.TestCase):
    def setUp(self):
        self.guide = GUIDE.read_text(encoding="utf-8")
        self.guide_flat = " ".join(self.guide.split())
        self.runtime = RUNTIME.read_text(encoding="utf-8")
        self.routing = ROUTING.read_text(encoding="utf-8")
        self.active_skill = ACTIVE_SKILL.read_text(encoding="utf-8")

    def test_route_fails_closed_without_a_reviewed_execution_service(self):
        self.assertIn("client-only", self.guide)
        self.assertIn("STOP: do not generate or install a Docker Python lab", self.guide)
        self.assertIn("scripts/run-python-docker.sh", self.guide)
        self.assertIn("does not ship the execution service", self.routing)
        preflight = self.active_skill.index("### 0.3 Run the Docker Python lab preflight")
        first_scaffold = self.active_skill.index("## Step 1B: Single-Sim Shortcut")
        self.assertLess(preflight, first_scaffold)
        self.assertIn("stop before running any scaffold command", self.active_skill)
        self.assertIn("filtered input file", self.active_skill)
        self.assertIn("Requests without learner-authored code execution", self.active_skill)

    def test_guide_defines_the_local_service_security_boundary(self):
        required_controls = (
            "127.0.0.1 only",
            "explicit allowlist of browser origins",
            "missing, and `null` origins are rejected",
            "Content-Type: application/json",
            "--network none",
            "--read-only",
            "--cap-drop=ALL",
            "no-new-privileges",
            "--memory",
            "--cpus",
            "--pids-limit",
            "--rm",
            "non-root",
            "rejects `--privileged`",
            "host PID/IPC/user namespace",
            "unconfined seccomp or AppArmor",
            "pinned by digest",
            "fixed argv array",
            "passed over standard input",
            "never interpolated into a host shell",
            "request bytes",
            "streamed output bytes",
            "execution time",
            "forcibly stops and removes the container",
            "queued requests",
            "concurrent containers",
        )
        for control in required_controls:
            with self.subTest(control=control):
                self.assertIn(control, self.guide_flat)

    def test_guide_does_not_promise_undeclared_packages(self):
        opening = self.guide.split("## Prerequisites", 1)[0]
        self.assertNotIn("third-party packages", opening)
        self.assertIn("standard library only", opening)

    def test_timing_ui_does_not_invent_one_way_network_measurements(self):
        forbidden = (
            "network-send",
            "network-return",
            "network_total / 2",
            "Send to service (network)",
            "Return to browser (network)",
        )
        for phrase in forbidden:
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase, self.guide)
                self.assertNotIn(phrase, self.runtime)
        self.assertIn("Browser and network overhead (combined)", self.guide)
        self.assertIn("roundtrip-overhead", self.runtime)

    def test_runtime_contains_a_consistency_checked_timing_boundary(self):
        self.assertIn("function _dockerTimingValue", self.runtime)
        self.assertIn("function _dockerTimingBreakdown", self.runtime)
        self.assertIn("container-overhead", self.runtime)
        self.assertIn("timing_consistent", self.runtime)


if __name__ == "__main__":
    unittest.main()
