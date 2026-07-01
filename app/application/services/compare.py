from dataclasses import dataclass

from app.domain.entities.phone import Phone
from app.shared.constants import MESSAGE_SEPARATOR


@dataclass
class CompareCategory:
    label: str
    values: list[str]
    winner_index: int | None


@dataclass
class CompareResult:
    phones: list[Phone]
    categories: list[CompareCategory]
    overall_winner_index: int
    overall_scores: list[float]


class PhoneCompareService:
    def compare(self, phones: list[Phone]) -> CompareResult:
        if len(phones) < 2:
            raise ValueError("Need at least 2 phones")

        categories: list[CompareCategory] = []
        wins = [0, 0]

        specs: list[tuple[str, list[float], str]] = [
            ("📷 Camera", [p.camera_score for p in phones], "score"),
            ("🔋 Battery", [p.battery_score for p in phones], "score"),
            ("🖥️ Display", [p.display_score for p in phones], "score"),
            ("⚡ Performance", [p.performance_score for p in phones], "score"),
            ("💰 Price", [-float(p.price) for p in phones], "price"),
            ("🧠 RAM", [float(p.ram_gb) for p in phones], "ram"),
            ("💾 Storage", [float(p.storage_gb) for p in phones], "storage"),
        ]

        for label, scores, fmt in specs:
            best = max(scores)
            winner = scores.index(best) if scores.count(best) == 1 else None
            if winner is not None:
                wins[winner] += 1

            if fmt == "price":
                display = [f"${p.price:,.0f}" for p in phones]
            elif fmt in ("ram", "storage"):
                field = "ram_gb" if fmt == "ram" else "storage_gb"
                display = [f"{getattr(p, field)}GB" for p in phones]
            else:
                display = [f"{s:.0f}/100" for s in scores]

            categories.append(CompareCategory(label=label, values=display, winner_index=winner))

        overall_winner = 0 if wins[0] >= wins[1] else 1
        overall_scores = [
            p.performance_score * 0.3
            + p.camera_score * 0.25
            + p.battery_score * 0.2
            + p.display_score * 0.25
            for p in phones
        ]

        return CompareResult(
            phones=phones,
            categories=categories,
            overall_winner_index=overall_winner,
            overall_scores=overall_scores,
        )

    def format_telegram(self, result: CompareResult) -> str:
        header = "  vs  ".join(f"<b>{p.name}</b>" for p in result.phones)
        lines = ["⚖️ <b>Comparison</b>", MESSAGE_SEPARATOR, header, ""]

        for cat in result.categories:
            vals = " | ".join(cat.values)
            mark = ""
            if cat.winner_index is not None:
                name = result.phones[cat.winner_index].name
                mark = f" ✅ <b>{name}</b>"
            lines.append(f"{cat.label}: {vals}{mark}")

        winner = result.phones[result.overall_winner_index]
        score = result.overall_scores[result.overall_winner_index]
        lines += [
            "",
            MESSAGE_SEPARATOR,
            f"🏆 <b>Overall:</b> {winner.name} ({score:.0f}/100)",
        ]
        return "\n".join(lines)
