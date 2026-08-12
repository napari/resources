from napari_resources.generate_logos import generate_logos


def test_gen_logos(tmp_path):
    generate_logos(tmp_path)
