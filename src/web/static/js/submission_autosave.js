// Autosave for submission editor
(function () {
    const DEFAULT_INTERVAL = 10 * 1000; // 10s
    let autosaveTimer = null;

    function getConfig() {
        return window.AUTOSAVE_CONFIG || {};
    }

    function fetchLatestDraft(assignmentId, csrfToken) {
        return fetch(`/api/drafts?assignment_id=${assignmentId}`, {
            credentials: 'same-origin'
        }).then(r => r.json());
    }

    function postDraft(assignmentId, content, metadata, csrfToken) {
        return fetch('/api/drafts', {
            method: 'POST',
            credentials: 'same-origin',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken || ''
            },
            body: JSON.stringify({ assignment_id: assignmentId, content, metadata }),
            keepalive: true
        }).then(r => r.json());
    }

    function restoreDraftIfAny(assignmentId, csrfToken) {
        const codeInput = document.getElementById('code');
        if (!codeInput) return;
        fetchLatestDraft(assignmentId, csrfToken)
            .then(data => {
                if (data && data.success && data.draft && data.draft.content) {
                    // Only restore if editor is empty
                    if (!codeInput.value.trim()) {
                        codeInput.value = data.draft.content || '';
                        codeInput.dispatchEvent(new Event('input'));
                    }
                }
            })
            .catch(() => {
                // ignore restore errors silently
            });
    }

    function startAutosave() {
        const cfg = getConfig();
        const assignmentId = cfg.assignmentId;
        const csrfToken = cfg.csrfToken;
        const interval = (cfg.intervalMs || DEFAULT_INTERVAL);
        const codeInput = document.getElementById('code');
        if (!assignmentId || !codeInput) return;

        // Debounced autosave on change
        let pending = false;
        let lastContent = '';
        const statusEl = document.getElementById('autosaveStatus');

        function setStatus(state, text) {
            if (!statusEl) return;
            statusEl.className = 'autosave-status ' + state;
            statusEl.textContent = text;
        }

        function doSave() {
            const content = codeInput.value;
            if (content === lastContent) return;
            pending = true;
            setStatus('saving', 'Saving...');
            postDraft(assignmentId, content, null, csrfToken)
                .then(resp => {
                    if (!resp || !resp.success) {
                        console.warn('Autosave failed', resp && resp.error);
                        setStatus('error', 'Save failed');
                    } else {
                        setStatus('ok', 'Saved');
                    }
                })
                .catch(err => {
                    console.warn('Autosave network error', err);
                    setStatus('error', 'Network error');
                })
                .finally(() => {
                    lastContent = content;
                    pending = false;
                    // Clear status back to ok after a short delay
                    setTimeout(() => {
                        if (statusEl && statusEl.classList.contains('ok')) setStatus('ok', 'Saved');
                    }, 2500);
                });
        }

        // Periodic timer
        autosaveTimer = setInterval(() => {
            if (!pending) doSave();
        }, interval);

        // Save on meaningful input (debounced)
        let debounceTimer = null;
        codeInput.addEventListener('input', () => {
            if (debounceTimer) clearTimeout(debounceTimer);
            debounceTimer = setTimeout(doSave, 1500);
        });

        // Expose manual save for Save Draft button
        window.saveDraftManual = function () {
            doSave();
        };

        // Save on unload
        window.addEventListener('beforeunload', () => {
            if (codeInput.value.trim()) {
                // synchronous navigator.sendBeacon would be ideal, but fallback to fetch with keepalive
                try {
                    navigator.sendBeacon && navigator.sendBeacon('/api/drafts', JSON.stringify({ assignment_id: assignmentId, content: codeInput.value }));
                } catch (e) {
                    // last-resort async call
                    fetch('/api/drafts', { method: 'POST', keepalive: true, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ assignment_id: assignmentId, content: codeInput.value }) });
                }
            }
        });
    }

    // Init when DOM ready
    document.addEventListener('DOMContentLoaded', function () {
        const cfg = getConfig();
        const assignmentId = cfg.assignmentId;
        const csrfToken = cfg.csrfToken;
        if (!assignmentId) return;
        restoreDraftIfAny(assignmentId, csrfToken);
        startAutosave();
    });
})();
