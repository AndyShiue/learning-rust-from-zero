// Shared by the English and Traditional Chinese mdBook editions.
(() => {
    "use strict";

    const SHARE_ORIGIN = "https://learning-rust-from-ze.ro";
    const GITHUB_PROJECT_PATH = "/learning-rust-from-zero";
    const rightButtons = document.querySelector("#mdbook-menu-bar .right-buttons");

    if (!rightButtons) {
        return;
    }

    const isTraditionalChinese = document.documentElement.lang === "zh-TW";
    const strings = isTraditionalChinese
        ? {
              label: "複製分享連結",
              copied: "已複製連結",
              failed: "無法複製連結",
          }
        : {
              label: "Copy share link",
              copied: "Link copied",
              failed: "Could not copy link",
          };

    function publicPath(pathname) {
        return pathname
            .replace(/(\/chapter\d+\/)\d+_([^/]+\.html)$/i, "$1$2")
            .replace(/(\/appendix\d+\/)[a-z]_([^/]+\.html)$/i, "$1$2");
    }

    function shareUrl() {
        const canonical = document.querySelector('link[rel="canonical"]');
        const source = new URL(canonical?.href || window.location.href);
        let pathname = source.pathname;

        if (pathname === GITHUB_PROJECT_PATH) {
            pathname = "/";
        } else if (pathname.startsWith(`${GITHUB_PROJECT_PATH}/`)) {
            pathname = pathname.slice(GITHUB_PROJECT_PATH.length);
        }

        const language = isTraditionalChinese ? "zh-TW" : "en";
        if (!pathname.match(/^\/(?:en|zh-TW)(?:\/|$)/)) {
            pathname = `/${language}${pathname.startsWith("/") ? "" : "/"}${pathname}`;
        }

        pathname = publicPath(pathname).replace(/\/index\.html$/, "/");
        return `${SHARE_ORIGIN}${pathname}${window.location.hash}`;
    }

    function legacyCopy(text) {
        const input = document.createElement("textarea");
        input.value = text;
        input.setAttribute("readonly", "");
        input.style.position = "fixed";
        input.style.opacity = "0";
        document.body.appendChild(input);
        input.select();
        const copied = document.execCommand("copy");
        input.remove();

        if (!copied) {
            throw new Error("Copy command failed");
        }
    }

    async function copy(text) {
        if (navigator.clipboard?.writeText) {
            try {
                await navigator.clipboard.writeText(text);
                return;
            } catch (_error) {
                // Fall through for browsers that expose Clipboard API but deny it.
            }
        }
        legacyCopy(text);
    }

    const button = document.createElement("button");
    button.id = "share-link-button";
    button.className = "icon-button";
    button.type = "button";
    button.title = strings.label;
    button.setAttribute("aria-label", strings.label);

    const icon = document.createElement("span");
    icon.className = "fa-svg";
    icon.setAttribute("aria-hidden", "true");
    // Font Awesome Free 6.2.0 "link" icon (CC BY 4.0).
    icon.innerHTML =
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 512">' +
        '<path d="M0 256C0 167.6 71.6 96 160 96h72c13.3 0 24 10.7 24 24s-10.7 24-24 24h-72C98.1 144 48 194.1 48 256s50.1 112 112 112h72c13.3 0 24 10.7 24 24s-10.7 24-24 24h-72C71.6 416 0 344.4 0 256zm640 0c0 88.4-71.6 160-160 160h-72c-13.3 0-24-10.7-24-24s10.7-24 24-24h72c61.9 0 112-50.1 112-112S541.9 144 480 144h-72c-13.3 0-24-10.7-24-24s10.7-24 24-24h72c88.4 0 160 71.6 160 160zM224 232h192c13.3 0 24 10.7 24 24s-10.7 24-24 24H224c-13.3 0-24-10.7-24-24s10.7-24 24-24z"/>' +
        "</svg>";

    const status = document.createElement("span");
    status.className = "tooltiptext share-link-tooltip";
    status.setAttribute("role", "status");
    status.setAttribute("aria-live", "polite");

    button.append(icon, status);
    rightButtons.prepend(button);

    let statusTimer;
    button.addEventListener("click", async () => {
        try {
            await copy(shareUrl());
            status.textContent = strings.copied;
        } catch (_error) {
            status.textContent = strings.failed;
        }

        button.classList.add("tooltipped");
        window.clearTimeout(statusTimer);
        statusTimer = window.setTimeout(() => {
            button.classList.remove("tooltipped");
        }, 1600);
    });
})();
