import 'package:flutter/material.dart';

/// Başlıklı içerik kartı.
class SectionCard extends StatelessWidget {
  final String? title;
  final IconData? icon;
  final List<Widget> children;
  final Widget? trailing;
  const SectionCard({super.key, this.title, this.icon, this.trailing, required this.children});

  @override
  Widget build(BuildContext context) {
    final t = Theme.of(context);
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (title != null)
              Row(
                children: [
                  if (icon != null) ...[
                    Icon(icon, size: 20, color: t.colorScheme.primary),
                    const SizedBox(width: 8),
                  ],
                  Expanded(
                    child: Text(title!,
                        style: t.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w700)),
                  ),
                  if (trailing != null) trailing!,
                ],
              ),
            if (title != null) const SizedBox(height: 12),
            ...children,
          ],
        ),
      ),
    );
  }
}

/// Etiket + değer küçük rozeti.
class StatChip extends StatelessWidget {
  final String label;
  final String value;
  final Color? color;
  const StatChip({super.key, required this.label, required this.value, this.color});

  @override
  Widget build(BuildContext context) {
    final t = Theme.of(context);
    final c = color ?? t.colorScheme.primary;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: c.withValues(alpha: 0.10),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(label, style: t.textTheme.labelSmall?.copyWith(color: t.colorScheme.onSurfaceVariant)),
          const SizedBox(height: 2),
          Text(value, style: t.textTheme.titleSmall?.copyWith(fontWeight: FontWeight.w700, color: c)),
        ],
      ),
    );
  }
}

/// Kalori ilerleme halkası (alınan / hedef).
class KcalRing extends StatelessWidget {
  final double intake;
  final double? target;
  const KcalRing({super.key, required this.intake, this.target});

  @override
  Widget build(BuildContext context) {
    final t = Theme.of(context);
    final pct = (target != null && target! > 0) ? (intake / target!).clamp(0.0, 1.0) : 0.0;
    final over = target != null && intake > target!;
    return SizedBox(
      width: 132,
      height: 132,
      child: Stack(
        alignment: Alignment.center,
        children: [
          SizedBox(
            width: 132,
            height: 132,
            child: CircularProgressIndicator(
              value: target != null ? pct : 0.0,
              strokeWidth: 11,
              backgroundColor: t.colorScheme.surfaceContainerHighest,
              valueColor: AlwaysStoppedAnimation(
                over ? t.colorScheme.error : t.colorScheme.primary,
              ),
              strokeCap: StrokeCap.round,
            ),
          ),
          Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(intake.toStringAsFixed(0),
                  style: t.textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.w800)),
              Text(target != null ? '/ ${target!.toStringAsFixed(0)} kcal' : 'kcal',
                  style: t.textTheme.bodySmall?.copyWith(color: t.colorScheme.onSurfaceVariant)),
            ],
          ),
        ],
      ),
    );
  }
}

/// Makro ilerleme çubuğu.
class MacroBar extends StatelessWidget {
  final String label;
  final double value;
  final double? target;
  final Color color;
  const MacroBar({super.key, required this.label, required this.value, this.target, required this.color});

  @override
  Widget build(BuildContext context) {
    final t = Theme.of(context);
    final pct = (target != null && target! > 0) ? (value / target!).clamp(0.0, 1.0) : null;
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(children: [
            Expanded(child: Text(label, style: t.textTheme.bodySmall)),
            Text(
              target != null ? '${value.toStringAsFixed(0)} / ${target!.toStringAsFixed(0)} g'
                              : '${value.toStringAsFixed(0)} g',
              style: t.textTheme.bodySmall?.copyWith(fontWeight: FontWeight.w600),
            ),
          ]),
          const SizedBox(height: 4),
          ClipRRect(
            borderRadius: BorderRadius.circular(6),
            child: LinearProgressIndicator(
              value: pct ?? 0.0,
              minHeight: 8,
              backgroundColor: color.withValues(alpha: 0.15),
              valueColor: AlwaysStoppedAnimation(color),
            ),
          ),
        ],
      ),
    );
  }
}

class LoadingView extends StatelessWidget {
  const LoadingView({super.key});
  @override
  Widget build(BuildContext context) =>
      const Center(child: Padding(padding: EdgeInsets.all(40), child: CircularProgressIndicator()));
}

class EmptyState extends StatelessWidget {
  final IconData icon;
  final String message;
  const EmptyState({super.key, required this.icon, required this.message});
  @override
  Widget build(BuildContext context) {
    final t = Theme.of(context);
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(40),
        child: Column(mainAxisSize: MainAxisSize.min, children: [
          Icon(icon, size: 56, color: t.colorScheme.outlineVariant),
          const SizedBox(height: 12),
          Text(message, textAlign: TextAlign.center,
              style: t.textTheme.bodyMedium?.copyWith(color: t.colorScheme.onSurfaceVariant)),
        ]),
      ),
    );
  }
}

class ErrorBanner extends StatelessWidget {
  final Object? error;
  const ErrorBanner(this.error, {super.key});
  @override
  Widget build(BuildContext context) {
    final t = Theme.of(context);
    return Card(
      color: t.colorScheme.errorContainer,
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Row(children: [
          Icon(Icons.error_outline, color: t.colorScheme.onErrorContainer),
          const SizedBox(width: 10),
          Expanded(
            child: Text('$error',
                style: TextStyle(color: t.colorScheme.onErrorContainer)),
          ),
        ]),
      ),
    );
  }
}
