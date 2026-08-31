document.addEventListener("DOMContentLoaded", function () {


    /*
     * =========================================================
     * MOBILE MENU
     * =========================================================
     */

    const menuButton =
        document.querySelector("[data-mobile-menu]");

    const sidebar =
        document.querySelector("[data-sidebar]");

    const overlay =
        document.querySelector("[data-sidebar-overlay]");


    function openMenu() {

        if (sidebar) {
            sidebar.classList.add("mobile-open");
        }

        if (overlay) {
            overlay.classList.add("active");
        }

        document.body.classList.add("menu-open");
    }


    function closeMenu() {

        if (sidebar) {
            sidebar.classList.remove("mobile-open");
        }

        if (overlay) {
            overlay.classList.remove("active");
        }

        document.body.classList.remove("menu-open");
    }


    if (menuButton) {

        menuButton.addEventListener(
            "click",
            openMenu
        );

    }


    if (overlay) {

        overlay.addEventListener(
            "click",
            closeMenu
        );

    }


    /*
     * Close mobile navigation after selecting a link.
     */

    if (sidebar) {

        sidebar
            .querySelectorAll("a")
            .forEach(link => {

                link.addEventListener(
                    "click",
                    closeMenu
                );

            });

    }


    /*
     * =========================================================
     * INSTALL PWA
     * =========================================================
     */

    let deferredPrompt = null;


    window.addEventListener(
        "beforeinstallprompt",
        function (event) {

            event.preventDefault();

            deferredPrompt = event;


            document
                .querySelectorAll("[data-install-app]")
                .forEach(button => {

                    button.style.display = "inline-flex";

                    button.addEventListener(
                        "click",
                        installApp
                    );

                });

        }
    );


    async function installApp() {

        if (!deferredPrompt) {
            return;
        }


        deferredPrompt.prompt();


        try {

            await deferredPrompt.userChoice;

        } catch (error) {

            console.error(
                "App installation error:",
                error
            );

        }


        deferredPrompt = null;


        document
            .querySelectorAll("[data-install-app]")
            .forEach(button => {

                button.style.display = "none";

            });

    }


    /*
     * App successfully installed.
     */

    window.addEventListener(
        "appinstalled",
        function () {

            deferredPrompt = null;


            document
                .querySelectorAll("[data-install-app]")
                .forEach(button => {

                    button.style.display = "none";

                });

        }
    );


    /*
     * =========================================================
     * SERVICE WORKER
     * =========================================================
     *
     * IMPORTANT:
     *
     * Actual file:
     *
     * /static/service-worker.js
     *
     * =========================================================
     */

    if ("serviceWorker" in navigator) {

        window.addEventListener(
            "load",
            function () {

                navigator.serviceWorker
                    .register(
                        "/static/service-worker.js"
                    )
                    .then(function (registration) {

                        console.log(
                            "Service Worker registered:",
                            registration.scope
                        );

                    })
                    .catch(function (error) {

                        console.error(
                            "Service Worker registration failed:",
                            error
                        );

                    });

            }
        );

    }


    /*
     * =========================================================
     * PREVENT DOUBLE SUBMISSION
     * =========================================================
     */

    document
        .querySelectorAll("form")
        .forEach(form => {

            form.addEventListener(
                "submit",
                function () {

                    const submitButtons =
                        form.querySelectorAll(
                            'button[type="submit"], input[type="submit"]'
                        );


                    submitButtons.forEach(button => {

                        if (
                            button.dataset.noDisable === "true"
                        ) {
                            return;
                        }


                        button.disabled = true;


                        const originalText =
                            button.innerHTML;


                        button.dataset.originalText =
                            originalText;


                        button.innerHTML =
                            "Processing...";

                    });

                }
            );

        });


    /*
     * =========================================================
     * AUTO HIDE FLASH MESSAGES
     * =========================================================
     */

    document
        .querySelectorAll("[data-auto-dismiss]")
        .forEach(message => {

            setTimeout(function () {

                message.classList.add(
                    "flash-hide"
                );


                setTimeout(function () {

                    message.remove();

                }, 300);

            }, 5000);

        });

});