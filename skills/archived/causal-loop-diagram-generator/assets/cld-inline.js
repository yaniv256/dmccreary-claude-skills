// Inline CLD renderer — used by the article pages to render multiple CLDs
// directly on the page (no iframes). Each diagram is a <div class="cld-inline"
// data-cld="<id>" data-src="<json url>"></div>.
//
// Why inline instead of iframes: the iframe approach hits a per-document
// rendering ceiling around the 6th instance in both Chrome and Firefox —
// vis-network silently never paints in later iframes. Sharing a single JS
// context makes that limit go away because there is only one document and
// one vis-network library load.

(function () {
    'use strict';

    const VIS_JS = 'https://unpkg.com/vis-network@10.0.1/standalone/umd/vis-network.min.js';

    let visLoading = null;
    function loadVisNetwork() {
        if (window.vis && window.vis.Network) return Promise.resolve();
        if (visLoading) return visLoading;
        visLoading = new Promise(function (resolve, reject) {
            const s = document.createElement('script');
            s.src = VIS_JS;
            s.async = true;
            s.onload = resolve;
            s.onerror = function () { reject(new Error('Failed to load vis-network')); };
            document.head.appendChild(s);
        });
        return visLoading;
    }

    function wrapText(text, maxLen) {
        if (!text || text.length <= maxLen) return text;
        const words = text.split(' ');
        const lines = [];
        let line = '';
        for (let i = 0; i < words.length; i++) {
            const w = words[i];
            if ((line + ' ' + w).trim().length <= maxLen) {
                line = (line ? line + ' ' : '') + w;
            } else {
                if (line) lines.push(line);
                line = w;
            }
        }
        if (line) lines.push(line);
        return lines.join('\n');
    }

    // Custom wheel-zoom: vertical scroll passes through (page scroll), horizontal
    // and pinch zoom the network. Matches the iframe viewer's behavior.
    function attachCustomZoom(container, network) {
        const ZOOM_PER_TICK = 0.04;
        const MIN_SCALE = 0.1;
        const MAX_SCALE = 5.0;
        container.addEventListener('wheel', function (event) {
            if (!network) return;
            const isPinch = event.ctrlKey;
            const dx = event.deltaX, dy = event.deltaY;
            const isHorizontalDominant = Math.abs(dx) > Math.abs(dy) && dx !== 0;
            if (!isPinch && !isHorizontalDominant) return;
            event.preventDefault();
            let delta = isPinch ? dy : dx;
            if (event.deltaMode === 1) delta *= 16;
            else if (event.deltaMode === 2) delta *= 400;
            if (delta === 0) return;
            const direction = delta < 0 ? 1 : -1;
            const magnitude = Math.min(Math.abs(delta), 60) / 60;
            const factor = 1 + direction * ZOOM_PER_TICK * magnitude;
            const oldScale = network.getScale();
            const newScale = Math.max(MIN_SCALE, Math.min(MAX_SCALE, oldScale * factor));
            if (newScale === oldScale) return;
            const rect = container.getBoundingClientRect();
            const pointerDom = { x: event.clientX - rect.left, y: event.clientY - rect.top };
            const pointerCanvas = network.DOMtoCanvas(pointerDom);
            const view = network.getViewPosition();
            const newView = {
                x: pointerCanvas.x - (pointerCanvas.x - view.x) * (oldScale / newScale),
                y: pointerCanvas.y - (pointerCanvas.y - view.y) * (oldScale / newScale)
            };
            network.moveTo({ scale: newScale, position: newView, animation: false });
        }, { passive: false });
    }

    // When a node sits near the top of the canvas its tooltip overlaps the
    // diagram title. This observer repositions the tooltip below the node
    // whenever vis-network places it inside the title safe zone (top 60 px).
    // Termination: after one flip the new top is >= SAFE_PX, so the recursive
    // observer fire finds the condition false and does nothing.
    function attachTooltipRepositioner(networkDiv) {
        const SAFE_PX = 60;
        const observer = new MutationObserver(function () {
            const tip = networkDiv.querySelector('.vis-tooltip');
            if (!tip) return;
            const top = parseFloat(tip.style.top) || 0;
            if (top < SAFE_PX) {
                const h = tip.offsetHeight || 80;
                tip.style.top = (top + h + 16) + 'px';
            }
        });
        observer.observe(networkDiv, {
            subtree: true,
            attributes: true,
            attributeFilter: ['style']
        });
    }

    // Returns a DOM element for vis-network tooltips. Passing a DOM node (not
    // a string) bypasses vis-network's internal white-space override, so the
    // text actually wraps instead of running off the canvas.
    function makeTooltip(text) {
        if (!text) return undefined;
        var div = document.createElement('div');
        div.style.cssText = 'max-width:260px;white-space:normal;word-wrap:break-word;overflow-wrap:break-word;line-height:1.5;font-size:13px;padding:2px 0;';
        div.textContent = text;
        return div;
    }

    function buildVisNodes(data) {
        const out = data.nodes.map(function (n) {
            return {
                id: n.id,
                label: wrapText(n.label, 18),
                x: n.position.x,
                y: n.position.y,
                title: makeTooltip(n.description || n.label)
            };
        });
        if (Array.isArray(data.loops)) {
            data.loops.forEach(function (loop) {
                if (!loop.position) return;
                out.push({
                    id: 'loop_' + loop.id,
                    label: loop.id,
                    x: loop.position.x,
                    y: loop.position.y,
                    shape: 'ellipse',
                    size: 26,
                    color: {
                        background: loop.type === 'reinforcing' ? '#dc3545' : '#28a745',
                        border: '#000'
                    },
                    font: { color: 'white', size: 16, face: 'Arial' },
                    widthConstraint: { minimum: 40, maximum: 40 },
                    heightConstraint: { minimum: 40, valign: 'middle' },
                    title: makeTooltip((loop.label || loop.id) + ': ' + (loop.description || ''))
                });
            });
        }
        return out;
    }

    function buildVisEdges(data) {
        return data.edges.map(function (e) {
            return {
                id: e.id,
                from: e.source,
                to: e.target,
                label: e.polarity === 'positive' ? '+' : '−',
                color: { color: e.polarity === 'positive' ? '#28a745' : '#dc3545' },
                title: makeTooltip(e.description || ''),
                font: {
                    size: 28,
                    color: e.polarity === 'positive' ? '#1e7e34' : '#a71d2a',
                    strokeWidth: 4,
                    strokeColor: 'white',
                    align: 'middle'
                },
                smooth: { type: 'curvedCW', roundness: 0.18 }
            };
        });
    }

    const NETWORK_OPTIONS = {
        layout: { improvedLayout: false },
        physics: { enabled: false },
        interaction: {
            selectConnectedEdges: false,
            zoomView: false,
            dragView: true,
            hover: true,
            tooltipDelay: 200
        },
        nodes: {
            shape: 'box',
            margin: 10,
            font: { size: 16, face: 'Arial' },
            borderWidth: 2,
            shadow: true,
            color: {
                background: 'white',
                border: 'dodgerblue',
                highlight: { background: 'lightskyblue', border: 'darkblue' }
            }
        },
        edges: {
            arrows: { to: { enabled: true, scaleFactor: 1.0 } },
            width: 2,
            smooth: { type: 'curvedCW', roundness: 0.18 }
        }
    };

    async function render(container) {
        if (container.dataset.rendered === '1') return;
        container.dataset.rendered = '1';

        const src = container.dataset.src;
        if (!src) {
            container.innerHTML = '<div style="padding:1em;color:#a71d2a">Missing data-src on .cld-inline element.</div>';
            return;
        }

        try {
            const [data] = await Promise.all([
                fetch(src).then(function (r) {
                    if (!r.ok) throw new Error('Failed to fetch ' + src + ' (' + r.status + ')');
                    return r.json();
                }),
                loadVisNetwork()
            ]);

            const networkDiv = document.createElement('div');
            networkDiv.style.position = 'absolute';
            networkDiv.style.inset = '0';
            container.appendChild(networkDiv);

            const network = new vis.Network(networkDiv, {
                nodes: new vis.DataSet(buildVisNodes(data)),
                edges: new vis.DataSet(buildVisEdges(data))
            }, NETWORK_OPTIONS);

            attachCustomZoom(networkDiv, network);
            attachTooltipRepositioner(networkDiv);

            // Title overlay
            const overlay = document.createElement('div');
            overlay.className = 'cld-inline-title';
            overlay.textContent = (data.metadata && data.metadata.title) || '';
            container.appendChild(overlay);

            network.fit({ animation: false });

            // Watch for size changes (e.g. responsive layout shifts) and refit.
            if ('ResizeObserver' in window) {
                let lastW = 0, lastH = 0;
                const ro = new ResizeObserver(function (entries) {
                    const r = entries[0].contentRect;
                    if (r.width <= 0 || r.height <= 0) return;
                    if (r.width === lastW && r.height === lastH) return;
                    lastW = r.width; lastH = r.height;
                    network.setSize(r.width + 'px', r.height + 'px');
                    network.redraw();
                });
                ro.observe(networkDiv);
            }
        } catch (err) {
            container.innerHTML = '<div style="padding:1em;color:#a71d2a">Failed to render CLD: ' + err.message + '</div>';
            container.dataset.rendered = '0';
        }
    }

    // Inject tooltip CSS once per page so vis-network tooltips wrap instead of
    // running off the edge of the canvas.
    let tooltipStyleInjected = false;
    function injectTooltipStyle() {
        if (tooltipStyleInjected) return;
        tooltipStyleInjected = true;
        const s = document.createElement('style');
        s.textContent = [
            '.vis-tooltip {',
            '  max-width: 280px;',
            '  white-space: normal;',
            '  word-wrap: break-word;',
            '  line-height: 1.5;',
            '  font-size: 13px;',
            '}'
        ].join('\n');
        document.head.appendChild(s);
    }

    function init() {
        const containers = document.querySelectorAll('.cld-inline[data-src]');
        if (!containers.length) return;
        injectTooltipStyle();

        if (!('IntersectionObserver' in window)) {
            containers.forEach(render);
            return;
        }

        const io = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    io.unobserve(entry.target);
                    render(entry.target);
                }
            });
        }, { rootMargin: '300px 0px', threshold: 0.01 });

        containers.forEach(function (c) { io.observe(c); });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
