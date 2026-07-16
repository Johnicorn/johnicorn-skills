from b3.normalize import normalize

def test_nfc_identity_for_precomposed_latvian():
    text = "Rīgā tiek nodrošināts atbalsts."
    norm, omap = normalize(text)
    assert norm == text                       # already NFC
    assert len(omap) == len(norm)
    assert omap[0] == 0 and omap[-1] == len(text) - 1

def test_offset_map_reverses_decomposed_input():
    # 'ī' as i + combining macron -> NFC composes to single 'ī'
    text = "ī"                           # decomposed ī
    norm, omap = normalize(text)
    assert norm == "ī"
    assert omap[0] == 0                        # normalized char 0 maps back to original start
