
def generate_quit_plan_txt(plan_data):
    if not isinstance(plan_data, dict):
        return "No quit plan data available."

    lines = []
    lines.append("MY QUIT PLAN")
    lines.append("=" * 40)
    lines.append("")

    for section, content in plan_data.items():
        lines.append(f"{section.upper()}")
        lines.append("-" * len(section))
        lines.append(content.strip())
        lines.append("")

    return "\n".join(lines)
