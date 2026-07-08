# -*- coding: utf-8 -*-

# About button for Family Content toolbar
# Place under: About.pushbutton/script.py

try:
    import clr

    clr.AddReference("PresentationFramework")
    clr.AddReference("PresentationCore")
    clr.AddReference("WindowsBase")

    from pyrevit import HOST_APP

    from System.Windows import (
        Window,
        Thickness,
        CornerRadius,
        WindowStartupLocation,
        ResizeMode,
        FontWeights,
        TextWrapping,
        HorizontalAlignment,
        VerticalAlignment
    )

    from System.Windows.Controls import (
        StackPanel,
        TextBlock,
        Button,
        Border
    )

    from System.Windows.Media import (
        SolidColorBrush,
        Color
    )


    # -----------------------------
    # Text
    # -----------------------------

    TOOLBAR_NAME = u"Family Content"
    TOOLBAR_VERSION = u"Revit 2025"
    COMPATIBILITY_TEXT = u"Compatible with Revit 2025 and newer."

    INTRO_TEXT = (
        u"Quick access to common, universal Revit families "
        u"so you do not have to search through folders."
    )

    CONTRIBUTE_TEXT = (
        u"If you have a clean, highly reusable family that could be useful on many project, "
        u"please feel free to share it with me. I will add it and credit you "
        u"as the contributor so more people can benefit from it."
    )


    # -----------------------------
    # Colors
    # -----------------------------

    WINDOW_BG = "#F4F4F4"
    CARD_BG = "#FFFFFF"
    BLACK = "#111111"
    DARK_GRAY = "#333333"
    MID_GRAY = "#777777"
    BORDER_GRAY = "#DDDDDD"
    YELLOW = "#F5C518"
    YELLOW_DARK = "#8A6D00"


    # -----------------------------
    # Helpers
    # -----------------------------

    def make_color(hex_value):
        h = hex_value.replace("#", "")
        return Color.FromRgb(
            int(h[0:2], 16),
            int(h[2:4], 16),
            int(h[4:6], 16)
        )


    def brush(hex_value):
        return SolidColorBrush(make_color(hex_value))


    def make_text(text, size, color_hex, bold=False, margin=None, wrap=False):
        tb = TextBlock()
        tb.Text = text
        tb.FontSize = size
        tb.Foreground = brush(color_hex)

        if bold:
            tb.FontWeight = FontWeights.Bold

        if margin:
            tb.Margin = margin

        if wrap:
            tb.TextWrapping = TextWrapping.Wrap
            tb.Width = 410

        return tb


    def get_current_revit_version():
        try:
            return u"Current session: Revit {0}".format(HOST_APP.version)
        except:
            return u"Current session: Revit version unavailable"


    # -----------------------------
    # Window
    # -----------------------------

    class AboutWindow(Window):
        def __init__(self):
            Window.__init__(self)

            self.Title = u"About {0}".format(TOOLBAR_NAME)
            self.Width = 560
            self.Height = 575
            self.ResizeMode = ResizeMode.NoResize
            self.WindowStartupLocation = WindowStartupLocation.CenterScreen
            self.Background = brush(WINDOW_BG)

            self.Content = self.build_ui()

        def build_ui(self):
            outer = Border()
            outer.Background = brush(WINDOW_BG)
            outer.Padding = Thickness(28)

            card = Border()
            card.Background = brush(CARD_BG)
            card.BorderBrush = brush(BORDER_GRAY)
            card.BorderThickness = Thickness(1)
            card.CornerRadius = CornerRadius(12)
            card.Padding = Thickness(30)

            stack = StackPanel()
            card.Child = stack

            # Version pill
            version_pill = Border()
            version_pill.Background = brush(YELLOW)
            version_pill.CornerRadius = CornerRadius(20)
            version_pill.Padding = Thickness(12, 5, 12, 5)
            version_pill.HorizontalAlignment = HorizontalAlignment.Left
            version_pill.Margin = Thickness(0, 0, 0, 18)

            version_text = make_text(
                TOOLBAR_VERSION,
                12,
                BLACK,
                True
            )

            version_pill.Child = version_text
            stack.Children.Add(version_pill)

            # Title
            title = make_text(
                TOOLBAR_NAME,
                30,
                BLACK,
                True,
                Thickness(0, 0, 0, 4)
            )
            stack.Children.Add(title)

            # Compatibility
            compatibility = make_text(
                COMPATIBILITY_TEXT,
                13,
                YELLOW_DARK,
                False,
                Thickness(0, 0, 0, 22)
            )
            stack.Children.Add(compatibility)

            # Yellow divider
            divider = Border()
            divider.Height = 1
            divider.Width = 500
            divider.Background = brush(YELLOW)
            divider.HorizontalAlignment = HorizontalAlignment.Left
            divider.Margin = Thickness(0, 0, 0, 24)
            stack.Children.Add(divider)

            # What is this
            intro_title = make_text(
                u"What is this?",
                15,
                BLACK,
                True,
                Thickness(0, 0, 0, 6)
            )
            stack.Children.Add(intro_title)

            intro = make_text(
                INTRO_TEXT,
                13,
                DARK_GRAY,
                False,
                Thickness(0, 0, 0, 22),
                True
            )
            intro.LineHeight = 20
            stack.Children.Add(intro)

            # Contribute
            contribute_title = make_text(
                u"Want to contribute?",
                15,
                BLACK,
                True,
                Thickness(0, 0, 0, 6)
            )
            stack.Children.Add(contribute_title)

            contribute = make_text(
                CONTRIBUTE_TEXT,
                13,
                DARK_GRAY,
                False,
                Thickness(0, 0, 0, 24),
                True
            )
            contribute.LineHeight = 20
            stack.Children.Add(contribute)

            # Current Revit
            session = make_text(
                get_current_revit_version(),
                11,
                MID_GRAY,
                False,
                Thickness(0, 0, 0, 22)
            )
            stack.Children.Add(session)

            # Close button
            close_btn = Button()
            close_btn.Content = u"Close"
            close_btn.Width = 88
            close_btn.Height = 30
            close_btn.Background = brush(YELLOW)
            close_btn.Foreground = brush(BLACK)
            close_btn.BorderThickness = Thickness(0)
            close_btn.FontWeight = FontWeights.Bold
            close_btn.HorizontalAlignment = HorizontalAlignment.Right
            close_btn.VerticalAlignment = VerticalAlignment.Center
            close_btn.Click += self.close_clicked

            stack.Children.Add(close_btn)

            outer.Child = card
            return outer

        def close_clicked(self, sender, args):
            self.Close()


    AboutWindow().ShowDialog()


except Exception as err:
    from pyrevit import script

    output = script.get_output()
    output.print_md("## Family Content About Button Error")
    output.print_md("The About UI failed to load.")
    output.print_md("```")
    output.print_md(str(err))
    output.print_md("```")