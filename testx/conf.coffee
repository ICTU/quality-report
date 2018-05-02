exports.config =
  directConnect: true
  specs: ['spec/*']

  capabilities:
    browserName: 'chrome'
    shardTestFiles: false
    maxInstances: 5
    chromeOptions:
      args: ["--no-sandbox", "--headless", "--disable-gpu", "--window-size=1024,800"]

  framework: 'jasmine'
  jasmineNodeOpts:
    silent: true
    defaultTimeoutInterval: 300000
    includeStackTrace: false

  baseUrl: 'http://localhost:2015'

  onPrepare: ->
    require '@ictu/testx'
    testx.objects.add 'objects.csv'
    beforeEach ->
      browser.ignoreSynchronization = true

