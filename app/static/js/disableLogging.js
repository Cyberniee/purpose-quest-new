// disable-logging.js
if (window.console) {
    const noop = function() {};
    console.log = noop;
    console.warn = noop;
    console.error = noop;
    console.info = noop;
    console.debug = noop;
}