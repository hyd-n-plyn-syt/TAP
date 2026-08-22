/*
 * Define the default GoldenLayout-based config
 *
 * TAP override of Evennia's stock config: adds a right-hand column with
 * the TAP Map (top) and TAP Comm (bottom) panes alongside Main and input.
 *
 * The contents of the global variable will be overwritten by what is in the
 * browser's localstorage after visiting this site. Clear
 * "evenniaGoldenLayoutSavedState" to return to this default.
 *
 * For full documentation on all of the keywords see:
 *         http://golden-layout.com/docs/Config.html
 *
 */
var goldenlayout_config = { // Global Variable used in goldenlayout.js init()
    content: [{
        type: "row",
        content: [{
            type: "column",
            width: 70,
            content: [{
                type: "component",
                componentName: "Main",
                isClosable: false, // remove the 'x' control to close this
                tooltip: "Main - drag to desired position.",
                componentState: {
                    types: "untagged",
                    updateMethod: "newlines",
                },
            }, {
                type: "component",
                componentName: "input",
                id: "inputComponent", // mark for ignore
                height: 20,  // percentage
                isClosable: false, // remove the 'x' control to close this
                tooltip: "Input - The last input in the layout is always the default.",
            }]
        }, {
            type: "column",
            width: 30,
            content: [{
                type: "component",
                componentName: "TAP Map",
                height: 50,
                isClosable: false,
                tooltip: "TAP Map - room map pane.",
                componentState: {}
            }, {
                type: "component",
                componentName: "TAP Comm",
                height: 50,
                isClosable: false,
                tooltip: "TAP Communication - Local/OOC/MudInfo tabs.",
                componentState: {}
            }]
        }]
    }]
};
