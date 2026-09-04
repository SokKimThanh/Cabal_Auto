                    card = box.master
                    card.config(highlightbackground="#D0D0D0", highlightthickness=1)
                    if hasattr(app, "_create_tooltip"):
                        app._create_tooltip(card, app._t("skill_strip.tooltip_placeholder"))

    def _apply_hunt_mode(self) -> None:
        return
