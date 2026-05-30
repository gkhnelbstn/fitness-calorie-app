import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

/// Uygulama teması — React tasarımıyla hizalı: yeşil accent, Manrope gövde +
/// Poppins başlık, yumuşak kartlar.
class AppTheme {
  static const seed = Color(0xFF16A34A); // yeşil (React --accent)

  static ThemeData light() => _build(Brightness.light);
  static ThemeData dark() => _build(Brightness.dark);

  static ThemeData _build(Brightness b) {
    final scheme = ColorScheme.fromSeed(seedColor: seed, brightness: b);
    final baseText = ThemeData(brightness: b).textTheme;
    // Gövde Manrope; başlıklar (display/headline/title) Poppins — React fontları.
    final textTheme = GoogleFonts.manropeTextTheme(baseText).copyWith(
      displayLarge: GoogleFonts.poppins(textStyle: baseText.displayLarge, fontWeight: FontWeight.w700),
      displayMedium: GoogleFonts.poppins(textStyle: baseText.displayMedium, fontWeight: FontWeight.w700),
      displaySmall: GoogleFonts.poppins(textStyle: baseText.displaySmall, fontWeight: FontWeight.w700),
      headlineMedium: GoogleFonts.poppins(textStyle: baseText.headlineMedium, fontWeight: FontWeight.w700),
      headlineSmall: GoogleFonts.poppins(textStyle: baseText.headlineSmall, fontWeight: FontWeight.w800),
      titleLarge: GoogleFonts.poppins(textStyle: baseText.titleLarge, fontWeight: FontWeight.w700),
    );
    return ThemeData(
      colorScheme: scheme,
      useMaterial3: true,
      textTheme: textTheme,
      scaffoldBackgroundColor: b == Brightness.light
          ? const Color(0xFFF6F8F6)
          : scheme.surface,
      cardTheme: CardThemeData(
        elevation: 0,
        clipBehavior: Clip.antiAlias,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        color: scheme.surface,
        margin: const EdgeInsets.symmetric(vertical: 6),
      ),
      appBarTheme: AppBarTheme(
        centerTitle: false,
        backgroundColor: scheme.surface,
        surfaceTintColor: Colors.transparent,
        elevation: 0,
        scrolledUnderElevation: 1,
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: scheme.surfaceContainerHighest.withValues(alpha: 0.4),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: BorderSide.none,
        ),
        contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
      ),
      filledButtonTheme: FilledButtonThemeData(
        style: FilledButton.styleFrom(
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
        ),
      ),
      chipTheme: ChipThemeData(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        side: BorderSide.none,
      ),
      navigationBarTheme: NavigationBarThemeData(
        backgroundColor: scheme.surface,
        indicatorColor: scheme.primaryContainer,
        labelBehavior: NavigationDestinationLabelBehavior.onlyShowSelected,
      ),
    );
  }
}
