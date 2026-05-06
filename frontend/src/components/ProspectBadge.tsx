import clsx from "clsx";

interface Props {
  score: number;
  size?: "sm" | "md";
}

export default function ProspectBadge({ score, size = "sm" }: Props) {
  const label =
    score >= 80 ? "HOT" : score >= 60 ? "WARM" : score >= 40 ? "POTENTIAL" : "LOW";

  const color =
    score >= 80
      ? "bg-red-500/20 text-red-400 border-red-500/30"
      : score >= 60
        ? "bg-orange-500/20 text-orange-400 border-orange-500/30"
        : score >= 40
          ? "bg-yellow-500/20 text-yellow-400 border-yellow-500/30"
          : "bg-gray-700/40 text-gray-500 border-gray-700";

  return (
    <span
      className={clsx(
        "inline-flex items-center gap-1 rounded-full border font-semibold tracking-wide",
        size === "sm" ? "px-2 py-0.5 text-xs" : "px-3 py-1 text-sm",
        color
      )}
    >
      {label}
      <span className="opacity-70">·</span>
      {score}
    </span>
  );
}
