from examples.rad_parslet import rad_parslet


def test_model_hash():
    model = rad_parslet.TinyMeanModel()
    h = rad_parslet._compute_model_hash(model)
    assert isinstance(h, str)
