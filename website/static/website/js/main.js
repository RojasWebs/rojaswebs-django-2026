const header = document.querySelector(".site-header");
const menuToggle = document.querySelector(".menu-toggle");
const nav = document.querySelector(".site-nav");
const navLinks = document.querySelectorAll('a[href^="#"]');
const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

menuToggle?.addEventListener("click", () => {
    const isOpen = nav.classList.toggle("open");
    menuToggle.setAttribute("aria-expanded", String(isOpen));
});

function easeInOutCubic(progress) {
    return progress < 0.5
        ? 4 * progress ** 3
        : 1 - Math.pow(-2 * progress + 2, 3) / 2;
}

navLinks.forEach((link) => {
    link.addEventListener("click", (event) => {
        const targetId = link.getAttribute("href");
        if (!targetId || targetId === "#") return;

        const target = document.querySelector(targetId);
        if (!target) return;

        nav.classList.remove("open");
        menuToggle?.setAttribute("aria-expanded", "false");

        if (prefersReducedMotion) return;

        event.preventDefault();

        const headerOffset = header?.offsetHeight ?? 0;
        const startPosition = window.scrollY;
        const targetPosition =
            target.getBoundingClientRect().top +
            window.scrollY -
            headerOffset;

        const distance = targetPosition - startPosition;
        const duration = 720;
        let startTime = null;

        function animateScroll(currentTime) {
            if (startTime === null) startTime = currentTime;

            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const easedProgress = easeInOutCubic(progress);

            window.scrollTo(0, startPosition + distance * easedProgress);

            if (progress < 1) {
                requestAnimationFrame(animateScroll);
            }
        }

        requestAnimationFrame(animateScroll);
    });
});

const revealObserver = new IntersectionObserver(
    (entries) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                entry.target.classList.add("is-visible");
                revealObserver.unobserve(entry.target);
            }
        });
    },
    { threshold: 0.14 }
);

document.querySelectorAll(".reveal-section").forEach((section) => {
    if (prefersReducedMotion) {
        section.classList.add("is-visible");
    } else {
        revealObserver.observe(section);
    }
});

const trackedSections = document.querySelectorAll("main section[id]");
const navigationItems = document.querySelectorAll(".site-nav a");

const activeSectionObserver = new IntersectionObserver(
    (entries) => {
        entries.forEach((entry) => {
            if (!entry.isIntersecting) return;

            navigationItems.forEach((item) => {
                item.classList.toggle(
                    "active",
                    item.getAttribute("href") === `#${entry.target.id}`
                );
            });
        });
    },
    {
        rootMargin: "-35% 0px -55% 0px",
        threshold: 0,
    }
);

trackedSections.forEach((section) => activeSectionObserver.observe(section));
