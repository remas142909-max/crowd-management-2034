"""
ai_engine.py – محرك الذكاء الاصطناعي لتحليل الكثافة
AI Engine – Crowd Density Analysis & Smart Recommendations
"""

import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from simulation import StadiumSimulation


# ──────────────────────────────────────────────────────────────────
# Thresholds
# ──────────────────────────────────────────────────────────────────
CRITICAL_DENSITY   = 12   # agents per cell → critical alert
WARNING_DENSITY    = 8    # agents per cell → warning alert
HOTSPOT_ZONE_RATIO = 0.15 # if >15% of zone cells are hotspots → zone-level alert


# ──────────────────────────────────────────────────────────────────
# Smart Recommendation Templates
# ──────────────────────────────────────────────────────────────────
RECOMMENDATIONS = {
    "north_critical": {
        "level": "critical",
        "title": "🚨 ازدحام حرج – المدخل الشمالي",
        "msg": "⚠️ الكثافة تجاوزت الحد الآمن في الجهة الشمالية. "
               "التوصية: فتح البوابات الاحتياطية الشمالية (B3, B4)، "
               "وتحويل التدفق نحو المداخل الشرقية والغربية فوراً."
    },
    "south_critical": {
        "level": "critical",
        "title": "🚨 ازدحام حرج – المدخل الجنوبي",
        "msg": "⚠️ تراكم حرج في الجهة الجنوبية. "
               "التوصية: تفعيل كوادر الإرشاد الميداني، "
               "وإعادة توجيه الجماهير عبر الممر الجنوبي الغربي."
    },
    "east_critical": {
        "level": "critical",
        "title": "🚨 ازدحام حرج – المدخل الشرقي",
        "msg": "⚠️ بؤرة ازدحام شديدة في القطاع الشرقي. "
               "التوصية: إغلاق بوابات الدخول الشرقية مؤقتاً "
               "وتحويل الجمهور نحو البوابات الغربية."
    },
    "west_critical": {
        "level": "critical",
        "title": "🚨 ازدحام حرج – المدخل الغربي",
        "msg": "⚠️ ازدحام شديد في القطاع الغربي. "
               "التوصية: تفعيل خطة التوزيع المتوازن (Balanced Routing) "
               "وإرسال تعزيزات أمنية لمنطقة الغرب."
    },
    "center_critical": {
        "level": "critical",
        "title": "🚨 ازدحام حرج – منطقة المركز",
        "msg": "⚠️ ضغط بشري خطير في منطقة المركز. "
               "التوصية: تفعيل بروتوكول الإخلاء الفوري "
               "وتوجيه الجمهور نحو مخارج الطوارئ في كلا الجهتين."
    },
    "north_warning": {
        "level": "warning",
        "title": "⚠️ تحذير كثافة – الشمال",
        "msg": "الكثافة في تصاعد بالجهة الشمالية. يُنصح بمراقبة الوضع "
               "وتجهيز فرق الإرشاد للتدخل السريع."
    },
    "south_warning": {
        "level": "warning",
        "title": "⚠️ تحذير كثافة – الجنوب",
        "msg": "كثافة متزايدة في الجنوب. فكّر في فتح ممرات بديلة "
               "وتوجيه المشجعين القادمين حديثاً."
    },
    "east_warning": {
        "level": "warning",
        "title": "⚠️ تحذير كثافة – الشرق",
        "msg": "مستوى الكثافة يقترب من الحد الأصفر في القطاع الشرقي."
    },
    "west_warning": {
        "level": "warning",
        "title": "⚠️ تحذير كثافة – الغرب",
        "msg": "مستوى الكثافة يقترب من الحد الأصفر في القطاع الغربي."
    },
    "center_warning": {
        "level": "warning",
        "title": "⚠️ تحذير – منطقة المركز",
        "msg": "الكثافة في المنطقة الوسطى في ارتفاع. راقب الوضع عن كثب."
    },
    "global_critical": {
        "level": "critical",
        "title": "🚨 تحذير عام – الكثافة الكلية حرجة",
        "msg": "الكثافة الإجمالية في الاستاد تجاوزت 80%. "
               "التوصية: وقف دخول جماهير جديدة مؤقتاً، "
               "وتفعيل نظام الإخلاء الجزئي للقطاعات الأكثر ازدحاماً."
    },
    "global_warning": {
        "level": "warning",
        "title": "⚠️ تحذير – الكثافة الكلية مرتفعة",
        "msg": "الكثافة الإجمالية تجاوزت 60%. "
               "ابدأ بإعادة التوجيه الاستباقي نحو المناطق الأقل ازدحاماً."
    },
}


# ──────────────────────────────────────────────────────────────────
class CrowdAIEngine:
    """
    Analyzes the stadium grid to detect dangerous crowd density zones
    and generates actionable smart alerts with recommendations.
    """

    def analyze(self, sim: "StadiumSimulation") -> list[dict]:
        """
        Run density analysis on the current grid state.
        Returns a list of alert dicts: {level, title, msg}
        """
        alerts = []
        grid = sim.grid
        rows, cols = sim.rows, sim.cols

        # ── 1. Zone Analysis ──────────────────────────────────────
        zone_slices = {
            "north":  (grid[:rows // 4, :],                            ),
            "south":  (grid[3 * rows // 4:, :],                        ),
            "east":   (grid[:, 3 * cols // 4:],                        ),
            "west":   (grid[:, :cols // 4],                            ),
            "center": (grid[rows // 4:3 * rows // 4, cols // 4:3 * cols // 4],),
        }

        for zone_name, (zone_grid,) in zone_slices.items():
            total_cells = zone_grid.size
            if total_cells == 0:
                continue

            critical_cells = int(np.sum(zone_grid >= CRITICAL_DENSITY))
            warning_cells  = int(np.sum(zone_grid >= WARNING_DENSITY))
            critical_ratio = critical_cells / total_cells
            warning_ratio  = warning_cells  / total_cells

            if critical_ratio >= HOTSPOT_ZONE_RATIO:
                key = f"{zone_name}_critical"
                if key in RECOMMENDATIONS:
                    alerts.append(RECOMMENDATIONS[key])
            elif warning_ratio >= HOTSPOT_ZONE_RATIO:
                key = f"{zone_name}_warning"
                if key in RECOMMENDATIONS:
                    alerts.append(RECOMMENDATIONS[key])

        # ── 2. Global Density Check ───────────────────────────────
        non_zero = grid[grid > 0]
        if len(non_zero) > 0:
            global_mean = float(np.mean(non_zero))
            if global_mean >= CRITICAL_DENSITY * 0.7:
                alerts.insert(0, RECOMMENDATIONS["global_critical"])
            elif global_mean >= WARNING_DENSITY * 0.7:
                if not any(a["level"] == "critical" for a in alerts):
                    alerts.insert(0, RECOMMENDATIONS["global_warning"])

        # ── 3. Hotspot Cell Detection ────────────────────────────
        hotspot_positions = np.argwhere(grid >= CRITICAL_DENSITY)
        if len(hotspot_positions) > 0 and len(alerts) < 5:
            worst_idx = np.argmax(grid)
            worst_r, worst_c = np.unravel_index(worst_idx, grid.shape)
            worst_count = int(grid[worst_r, worst_c])
            if worst_count >= CRITICAL_DENSITY:
                alerts.append({
                    "level": "critical",
                    "title": f"📍 بؤرة ازدحام حرجة – خلية ({worst_r}, {worst_c})",
                    "msg": f"كثافة بالغة: {worst_count} مشجع في خلية واحدة. "
                           "التوصية: إرسال مرشدين ميدانيين فورًا لتشتيت الحشد."
                })

        # De-duplicate alerts by title
        seen = set()
        unique = []
        for a in alerts:
            if a["title"] not in seen:
                seen.add(a["title"])
                unique.append(a)

        return unique[:5]   # max 5 alerts at once
