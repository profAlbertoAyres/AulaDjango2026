/* ==========================================================================
   PersonalPro - Admin JS
   Controle de interações do layout administrativo
   ========================================================================== */

document.addEventListener("DOMContentLoaded", function () {
    var appWrapper = document.querySelector(".app-wrapper");
    var toggleBtn = document.querySelector(".btn-toggle-sidebar");
    var overlay = document.querySelector(".sidebar-overlay");

    /* ----------------------------------------------------------------------
       1. Alternar sidebar (colapsar no desktop / abrir-fechar no mobile)
       ---------------------------------------------------------------------- */
    function isMobile() {
        return window.innerWidth <= 991.98;
    }

    function toggleSidebar() {
        if (!appWrapper) return;

        if (isMobile()) {
            appWrapper.classList.toggle("sidebar-mobile-open");
        } else {
            appWrapper.classList.toggle("sidebar-collapsed");
            localStorage.setItem(
                "sidebarCollapsed",
                appWrapper.classList.contains("sidebar-collapsed")
            );
        }
    }

    if (toggleBtn) {
        toggleBtn.addEventListener("click", toggleSidebar);
    }

    if (overlay) {
        overlay.addEventListener("click", function () {
            appWrapper.classList.remove("sidebar-mobile-open");
        });
    }

    /* ----------------------------------------------------------------------
       2. Restaurar estado da sidebar salvo (apenas desktop)
       ---------------------------------------------------------------------- */
    if (!isMobile() && localStorage.getItem("sidebarCollapsed") === "true") {
        appWrapper.classList.add("sidebar-collapsed");
    }

    /* ----------------------------------------------------------------------
       3. Fechar sidebar mobile ao redimensionar para desktop
       ---------------------------------------------------------------------- */
    window.addEventListener("resize", function () {
        if (!isMobile()) {
            appWrapper.classList.remove("sidebar-mobile-open");
        }
    });

    /* ----------------------------------------------------------------------
       4. Fechar alertas do Django automaticamente após alguns segundos
       ---------------------------------------------------------------------- */
    var alerts = document.querySelectorAll(".alert-dismissible");
    alerts.forEach(function (alert) {
        setTimeout(function () {
            var bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            bsAlert.close();
        }, 6000);
    });

    /* ----------------------------------------------------------------------
       5. Ativar item do menu correspondente à URL atual
       ---------------------------------------------------------------------- */
    var currentPath = window.location.pathname;
    var navLinks = document.querySelectorAll(".sidebar-nav a.nav-link[href]");

    navLinks.forEach(function (link) {
        if (link.getAttribute("href") === currentPath) {
            link.classList.add("active");

            // Se estiver dentro de um submenu, expande o menu pai
            var parentCollapse = link.closest(".collapse");
            if (parentCollapse) {
                parentCollapse.classList.add("show");
                var parentToggle = document.querySelector(
                    '[data-bs-target="#' + parentCollapse.id + '"]'
                );
                if (parentToggle) {
                    parentToggle.classList.add("active");
                    parentToggle.setAttribute("aria-expanded", "true");
                }
            }
        }
    });
});