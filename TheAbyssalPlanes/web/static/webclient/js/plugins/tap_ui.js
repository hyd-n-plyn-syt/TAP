/*
 *
 * TAP UI plugin - Map and Communication panes for the Evennia webclient.
 * Mirrors the Mudlet package's windows:
 *   TAP Map  <- map-frame blocks captured from the text stream
 *              (/===\ ... \===/), plus server OOB "room_map" fallback.
 *   TAP Comm <- server OOB "comm_local" / "comm_OOC" / "comm_system"
 *               {sender: ..., message: ...} (message pre-converted to
 *               ANSI server-side).
 *
 * Includes full ANSI SGR parsing (16-color, xterm-256, truecolor) and an
 * Evennia pipe-code -> ANSI converter so everything renders identically
 * to Mudlet.
 *
 * REQUIRES: goldenlayout.js (must load BEFORE it in base.html)
 */
let tap_ui = (function () {

    var TAP_COMM_TAB_KEY = "tapCommActiveTab";
    var ESC = "\x1b[";

    // live pane references
    var mapDivs = [];
    var commDivs = [];

    // buffers for messages arriving before any pane exists
    var lastTextMap = null;

    // ------------------------------------------------------------------
    // Evennia pipe codes -> ANSI escapes
    // ------------------------------------------------------------------

    var PIPE_FG_BRIGHT = { r: 91, g: 92, y: 93, b: 94, m: 95, c: 96, w: 97, x: 90 };
    var PIPE_FG_DARK   = { R: 31, G: 32, Y: 33, B: 34, M: 35, C: 36, W: 37, X: 30 };

    function hexToRgb(hex) {
        return parseInt(hex.substr(0, 2), 16) + ";"
             + parseInt(hex.substr(2, 2), 16) + ";"
             + parseInt(hex.substr(4, 2), 16);
    }

    // grey letter a->16, b..y -> 232..255, z -> 231 (Evennia's mapping)
    function greyCode(ch) {
        if (ch === "a") return 16;
        if (ch === "z") return 231;
        return 230 + (ch.charCodeAt(0) - 96);
    }

    var pipe2ansi = function (text) {
        var out = "";
        var i = 0;
        while (i < text.length) {
            var ch = text.charAt(i);
            if (ch !== "|" || i === text.length - 1) {
                out += ch;
                i++;
                continue;
            }
            var next = text.charAt(i + 1);
            if (next === "|") {           // literal pipe
                out += "|";
                i += 2;
                continue;
            }
            if (next === "[") {
                var n2 = text.charAt(i + 2);
                if (n2 === "=" && i + 3 < text.length) {          // |[=a grey bg
                    out += ESC + "48;5;" + greyCode(text.charAt(i + 3)) + "m";
                    i += 4;
                    continue;
                }
                if (/[0-5]/.test(n2) && /^[0-5][0-5][0-5]/.test(text.substring(i + 2, i + 5))) {
                    var g = text.substring(i + 2, i + 5);
                    var code = 16 + (+g.charAt(0)) * 36 + (+g.charAt(1)) * 6 + (+g.charAt(2));
                    out += ESC + "48;5;" + code + "m";
                    i += 5;
                    continue;
                }
                var bgch = text.charAt(i + 2);
                if (PIPE_FG_DARK.hasOwnProperty(bgch)) {          // |[R dark bg
                    out += ESC + (PIPE_FG_DARK[bgch] + 10) + "m";
                    i += 3;
                    continue;
                }
                if (PIPE_FG_BRIGHT.hasOwnProperty(bgch)) {        // |[r bright bg
                    out += ESC + (PIPE_FG_BRIGHT[bgch] + 10) + "m";
                    i += 3;
                    continue;
                }
                if (n2 === "#" && /^[0-9a-fA-F]{6}/.test(text.substring(i + 3, i + 9))) {
                    out += ESC + "48;2;" + hexToRgb(text.substring(i + 3, i + 9)) + "m";
                    i += 9;
                    continue;
                }
                out += ch;                                        // unknown |[.. literal
                i++;
                continue;
            }
            if (next === "=" && i + 2 < text.length) {            // |=a grey fg
                out += ESC + "38;5;" + greyCode(text.charAt(i + 2)) + "m";
                i += 3;
                continue;
            }
            if (/[0-5][0-5][0-5]/.test(text.substring(i + 1, i + 4))) {   // |535 cube fg
                var gg = text.substring(i + 1, i + 4);
                var cc = 16 + (+gg.charAt(0)) * 36 + (+gg.charAt(1)) * 6 + (+gg.charAt(2));
                out += ESC + "38;5;" + cc + "m";
                i += 4;
                continue;
            }
            if (next === "#" && /^[0-9a-fA-F]{6}/.test(text.substring(i + 2, i + 8))) {   // |#rrggbb truecolor
                out += ESC + "38;2;" + hexToRgb(text.substring(i + 2, i + 8)) + "m";
                i += 8;
                continue;
            }
            if (PIPE_FG_BRIGHT.hasOwnProperty(next)) {            // |r bright fg
                out += ESC + PIPE_FG_BRIGHT[next] + "m";
                i += 2;
                continue;
            }
            if (PIPE_FG_DARK.hasOwnProperty(next)) {              // |R dark fg
                out += ESC + PIPE_FG_DARK[next] + "m";
                i += 2;
                continue;
            }
            if (next === "n") { out += ESC + "0m"; i += 2; continue; }
            if (next === "u") { out += ESC + "4m"; i += 2; continue; }
            if (next === "/") { out += "\n"; i += 2; continue; }
            // unknown token: pass through literally (same as telnet clients see)
            out += ch;
            i++;
        }
        return out;
    };

    // ------------------------------------------------------------------
    // ANSI SGR -> HTML
    // ------------------------------------------------------------------

    var palette16 = [
        "#000000", "#800000", "#008000", "#808000",
        "#000080", "#800080", "#008080", "#c0c0c0",
        "#808080", "#ff0000", "#00ff00", "#ffff00",
        "#0000ff", "#ff00ff", "#00ffff", "#ffffff"
    ];

    function xterm256(n) {
        if (n < 16) return palette16[n];
        if (n < 232) {
            var i = n - 16;
            var steps = [0, 95, 135, 175, 215, 255];
            return "rgb(" + steps[Math.floor(i / 36)] + ","
                           + steps[Math.floor((i % 36) / 6)] + ","
                           + steps[i % 6] + ")";
        }
        var v = 8 + (n - 232) * 10;
        return "rgb(" + v + "," + v + "," + v + ")";
    }

    function brighten(hex) {
        for (var i = 0; i < 8; i++) {
            if (palette16[i] === hex) return palette16[i + 8];
        }
        return hex;
    }

    function htmlEscape(text) {
        return text.replace(/&/g, "&amp;")
                   .replace(/</g, "&lt;")
                   .replace(/>/g, "&gt;");
    }

    var ansi2html = function (text) {
        var out = "";
        var fg = null, bg = null;
        var bold = false, underline = false, italic = false;

        function style() {
            var css = [];
            var fgc = fg;
            if (fgc && bold && fgc.charAt(0) === "#" && fgc.length === 7) {
                fgc = brighten(fgc);
            }
            if (bold) css.push("font-weight:bold");
            if (italic) css.push("font-style:italic");
            if (underline) css.push("text-decoration:underline");
            if (fgc) css.push("color:" + fgc);
            if (bg) css.push("background-color:" + bg);
            return "<span" + (css.length ? " style=\"" + css.join(";") + "\"" : "") + ">";
        }

        var parts = text.split(/(\x1b\[[0-9;]*m)/);
        for (var i = 0; i < parts.length; i++) {
            var part = parts[i];
            var m = part.match(/^\x1b\[([0-9;]*)m$/);
            if (m) {
                var codes = m[1] === "" ? ["0"] : m[1].split(";");
                for (var c = 0; c < codes.length; c++) {
                    var n = parseInt(codes[c], 10);
                    if (isNaN(n)) continue;
                    if (n === 0) {
                        fg = null; bg = null; bold = false; underline = false; italic = false;
                    } else if (n === 1) bold = true;
                    else if (n === 2) bold = false;
                    else if (n === 3) italic = true;
                    else if (n === 4) underline = true;
                    else if (n === 22) bold = false;
                    else if (n === 23) italic = false;
                    else if (n === 24) underline = false;
                    else if (n >= 30 && n <= 37) fg = palette16[n - 30];
                    else if (n === 39) fg = null;
                    else if (n >= 40 && n <= 47) bg = palette16[n - 40];
                    else if (n === 49) bg = null;
                    else if (n >= 90 && n <= 97) fg = palette16[n - 90 + 8];
                    else if (n >= 100 && n <= 107) bg = palette16[n - 100 + 8];
                    else if (n === 38 || n === 48) {
                        var mode = codes[c + 1];
                        var col = null;
                        if (mode === "5" && c + 2 < codes.length) {
                            col = xterm256(parseInt(codes[c + 2], 10));
                            c += 2;
                        } else if (mode === "2" && c + 4 < codes.length) {
                            col = "rgb(" + parseInt(codes[c + 2], 10) + ","
                                        + parseInt(codes[c + 3], 10) + ","
                                        + parseInt(codes[c + 4], 10) + ")";
                            c += 4;
                        }
                        if (col !== null) {
                            if (n === 38) fg = col; else bg = col;
                        }
                    }
                }
            } else if (part !== "") {
                out += style() + htmlEscape(part) + "</span>";
            }
        }
        return out;
    };

    // pipes -> ANSI -> HTML, in one go
    var renderAnsi = function (rawText) {
        return ansi2html(pipe2ansi(String(rawText)));
    };

    // ------------------------------------------------------------------
    // Font syncing (match main window / font.js plugin)
    // ------------------------------------------------------------------

    function fontCss() {
        var fam = localStorage.getItem("evenniaFontFamily");
        var size = localStorage.getItem("evenniaFontSize");
        var cs = window.getComputedStyle(document.body);
        var css = {};
        if (fam) css["font-family"] = fam;
        if (size) css["font-size"] = size + "em";
        return css;
    }

    function applyFonts() {
        var css = fontCss();
        if (!css["font-family"]) return;
        $(".tap-map").css(css);
        $(".tap-comm").css(css);
    }

    // watch for font changes made through the options dialog
    var fontObserver = null;
    function watchBodyFont() {
        if (fontObserver || !window.MutationObserver) return;
        fontObserver = new MutationObserver(applyFonts);
        fontObserver.observe(document.body, { attributes: true, attributeFilter: ["style"] });
    }

    // ------------------------------------------------------------------
    // Map pane plumbing
    // ------------------------------------------------------------------

    var mapBuffer = null;

    // Replace the map content entirely (like Mudlet's clearWindow+append).
    function setMap(html) {
        if (mapDivs.length === 0) {
            mapBuffer = html;
            return;
        }
        for (var i = 0; i < mapDivs.length; i++) {
            var div = mapDivs[i];
            div.html(html);
            div.scrollTop(0);
        }
    }

    function flushMapBuffer() {
        if (mapBuffer !== null && mapDivs.length > 0) {
            var html = mapBuffer;
            mapBuffer = null;
            setMap(html);
        }
    }

    // ------------------------------------------------------------------
    // Map capture from the text stream (Mudlet TAP_Map_Top/Bottom parity)
    // ------------------------------------------------------------------

    var mapPending = null;

    // The v1.evennia.com wire format delivers text as HTML
    // (parse_html output). Recover plain pipe-coded text for matching
    // and rendering.
    function plainize(s) {
        return s.replace(/<[^>]+>/g, "")
                .replace(/&#124;/g, "|")
                .replace(/&nbsp;/g, " ")
                .replace(/&lt;/g, "<")
                .replace(/&gt;/g, ">")
                .replace(/&quot;/g, "\"")
                .replace(/&apos;/g, "'")
                .replace(/&amp;/g, "&");
    }

    // strip pipe codes and ANSI escapes so frame patterns can be matched
    // regardless of leading/trailing color codes (Mudlet matches display
    // lines, which already have them stripped)
    function stripCodes(s) {
        return s.replace(/\x1b\[[0-9;]*m/g, "").replace(/\|(?:\[(?:=?[a-z]|[0-5](?=[0-5][0-5])|#)|[=#]?[^\s|])?/g, "");
    }

    function normalized(s) {
        return stripCodes(plainize(String(s))).replace(/\s+/g, " ").trim();
    }

    function isMapStart(s) { return /^\s*\/={3,}\\/.test(stripCodes(plainize(s))); }
    function isMapEnd(s) { return /\\={3,}\/\s*$/.test(stripCodes(plainize(s))); }

    function renderCapturedMap(text) {
        lastTextMap = normalized(text);
        setMap(renderAnsi(plainize(text)));
        flushMapBuffer();
    }

    var onText = function (args, kwargs) {
        if (!args || !args.length) return false;
        var text = String(args[0]);

        if (mapPending !== null) {
            mapPending += "\n" + text;
            if (isMapEnd(text)) {
                renderCapturedMap(mapPending);
                mapPending = null;
            }
            return true;
        }
        if (isMapStart(text)) {
            if (isMapEnd(text)) {
                renderCapturedMap(text);
            } else {
                mapPending = text;
            }
            return true;
        }
        return false;
    };

    // ------------------------------------------------------------------
    // Comm pane plumbing
    // ------------------------------------------------------------------

    var commTabs = ["local", "ooc", "mudinfo"];
    var tabLabels = { local: "Local", ooc: "OOC", mudinfo: "MudInfo" };
    var tabColors = { local: "comm_local", ooc: "comm_ooc", mudinfo: "comm_mudinfo" };

    function getActiveTab() {
        var t = localStorage.getItem(TAP_COMM_TAB_KEY);
        return commTabs.indexOf(t) !== -1 ? t : "local";
    }

    function buildCommComponent(container) {
        var root = $("<div class='tap-comm'></div>").css({
            "display": "flex",
            "flex-direction": "column",
            "height": "100%",
            "background-color": "black"
        });

        var header = $("<div class='tap-comm-tabs'></div>").css({
            "display": "flex",
            "flex": "0 0 auto",
            "height": "25px"
        });

        var content = $("<div class='tap-comm-content'></div>").css({
            "flex": "1 1 auto",
            "overflow-y": "auto",
            "overflow-x": "hidden",
            "white-space": "pre-wrap",
            "word-wrap": "break-word",
            "padding": "2px"
        });

        var active = getActiveTab();
        var current = active;

        var tabDivs = {};
        $.each(commTabs, function (idx, tab) {
            var tabdiv = $("<div class='tap-tab' data-tab='" + tab + "'></div>")
                .text(" " + tabLabels[tab] + " ")
                .css({
                    "width": "33.3%",
                    "cursor": "pointer",
                    "text-align": "center",
                    "user-select": "none"
                });
            tabDivs[tab] = tabdiv;
            header.append(tabdiv);
        });

        function setActive(tab) {
            localStorage.setItem(TAP_COMM_TAB_KEY, tab);
            current = tab;
            $.each(commTabs, function (idx, t) {
                var on = (t === tab);
                tabDivs[t].css("background-color", on ? "#808080" : "#555555")
                          .css("color", "#ffffff");
            });
            content.children(".tap-buf").hide();
            content.children(".buf-" + tab).show();
            scrollContent();
        }

        function scrollContent() {
            content.scrollTop(content.prop("scrollHeight"));
        }

        $.each(commTabs, function (idx, tab) {
            $("<div class='tap-buf buf-" + tab + " " + tabColors[tab] + "'></div>")
                .appendTo(content)
                .css("min-height", "1em");
        });

        $.each(commTabs, function (idx, tab) {
            tabDivs[tab].on("click", function () { setActive(tab); });
        });

        root.append(header).append(content);
        container.getElement().append(root);

        var ref = {
            show: function (tab, html) {
                content.children(".buf-" + tab).append(html);
                if (tab === current) {
                    scrollContent();
                }
            }
        };
        commDivs.push(ref);
        setActive(active);

        container.on("destroy", function () {
            var idx = commDivs.indexOf(ref);
            if (idx !== -1) commDivs.splice(idx, 1);
        });
    }

    function appendComm(tab, kwargs) {
        var message = (kwargs && kwargs.message !== undefined) ? String(kwargs.message) : "";
        var html = renderAnsi(message) + "\n";
        for (var i = 0; i < commDivs.length; i++) {
            commDivs[i].show(tab, html);
        }
    }

    // ------------------------------------------------------------------
    // OOB message claiming
    // ------------------------------------------------------------------

    var onUnknownCmd = function (cmdname, args, kwargs) {
        // Mudlet-only install message; the webclient doesn't need it.
        if (cmdname === "client_GUI") return true;
        if (cmdname === "room_map") {
            var mapText = null;
            if (kwargs && kwargs.map !== undefined) mapText = kwargs.map;
            else if (args && args.length > 0 && args[0] && args[0].map !== undefined) mapText = args[0].map;
            if (mapText === null) return true;
            // the text-stream capture already rendered this exact block
            if (normalized(mapText) !== lastTextMap) {
                setMap(ansi2html(String(mapText)));
                flushMapBuffer();
            }
            return true;
        }
        if (cmdname === "comm_local") { appendComm("local", kwargs); return true; }
        if (cmdname === "comm_OOC")   { appendComm("ooc", kwargs); return true; }
        if (cmdname === "comm_system"){ appendComm("mudinfo", kwargs); return true; }
        return false;
    };

    // ------------------------------------------------------------------
    // GoldenLayout component registration
    // ------------------------------------------------------------------

    var onLayoutChanged = function () {
        if (!window.plugins["goldenlayout"]) return;
        var myLayout = window.plugins["goldenlayout"].getGL();

        myLayout.registerComponent("TAP Map", function (container, componentState) {
            var div = $("<div class='tap-map'></div>").css({
                "background-color": "black",
                "height": "100%",
                "overflow-y": "auto",
                "overflow-x": "hidden",
                "white-space": "pre-wrap",
                "word-wrap": "break-word",
                "padding": "2px",
                "min-height": "1em"
            }).appendTo(container.getElement());

            mapDivs.push(div);

            container.on("destroy", function () {
                var idx = mapDivs.indexOf(div);
                if (idx !== -1) mapDivs.splice(idx, 1);
            });

            applyFonts();
            flushMapBuffer();
        });

        myLayout.registerComponent("TAP Comm", function (container, componentState) {
            buildCommComponent(container);
            applyFonts();
        });
    };

    var init = function () {
        console.log('TAP UI plugin initialized');
        // Guard against stale/corrupted saved layouts: if the browser has a
        // cached GoldenLayout state without the TAP panes (e.g. saved while
        // the plugin failed to load), drop it so the default config - which
        // includes them - is used instead. Runs before goldenlayout.js's
        // init() reads localStorage because this file loads first.
        try {
            var raw = localStorage.getItem("evenniaGoldenLayoutSavedState");
            if (raw) {
                var s = JSON.stringify(JSON.parse(raw));
                if (s.indexOf("TAP Map") === -1 || s.indexOf("TAP Comm") === -1) {
                    localStorage.removeItem("evenniaGoldenLayoutSavedState");
                    localStorage.removeItem("evenniaGoldenLayoutSavedStateName");
                }
            }
        } catch (e) {
            localStorage.removeItem("evenniaGoldenLayoutSavedState");
            localStorage.removeItem("evenniaGoldenLayoutSavedStateName");
        }
    };

    var postInit = function () {
        // register our components before goldenlayout.postInit calls
        // myLayout.init() (postInits run in script-load order, and this
        // file loads BEFORE goldenlayout.js).
        if (window.plugins["goldenlayout"]) {
            onLayoutChanged();
            watchBodyFont();
        }
    };

    return {
        init: init,
        postInit: postInit,
        onLayoutChanged: onLayoutChanged,
        onUnknownCmd: onUnknownCmd,
        onText: onText,
    }
})();
window.plugin_handler.add("tap_ui", tap_ui);
