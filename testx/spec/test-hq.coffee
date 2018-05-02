describe 'The test runner', ->
  it 'should be able to see the rendered hq report', ->
    testx.run 'script/hq.testx', 'Test',
      project: 'Voorbeeldproje...'
