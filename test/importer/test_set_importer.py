import importer.set_importer

def test_normalizeStringForDb_doesNothingForASCIIStrings():
  assert 'Nicol Bolas, the Ravager' == importer.set_importer.normalizeStringForDb('Nicol Bolas, the Ravager')

def test_normalizeStringForDb_replacesKnownBadCharacters():
  assert '-3: Destroy target creature' == importer.set_importer.normalizeStringForDb(u'\u22123: Destroy target creature')
  assert 'Creature - Dragon' == importer.set_importer.normalizeStringForDb(u'Creature \u2014 Dragon')
  assert '* Tap target creature' == importer.set_importer.normalizeStringForDb(u'\u2022 Tap target creature')