from kivymd.uix.slider import MDSlider
from text_conversion_functions import convert_seconds_to_text


class CustomMDSlider(MDSlider):
    """

    """
    def on_value_pos(self, *args) -> None:
        """
        Fired when the `value_pos` value changes.
        Sets a new value for the value label texture.
        """

        self._update_points()

        if self._value_label and self._value_container:
            # FIXME: I do not know how else I can update the texture.
            self._value_label.text = ""
            self._value_label.text = f"{convert_seconds_to_text(int(self.value))}"
            self._value_label.texture_update()
            label_value_rect = self._value_container.canvas.get_group(
                "md-slider-label-value-rect"
            )[0]
            label_value_rect.texture = None
            label_value_rect.texture = self._value_label.texture
            label_value_rect.size = self._value_label.texture_size