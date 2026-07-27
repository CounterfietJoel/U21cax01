"use strict";

function activateTab(interaction, control, moveFocus = false) {
  const controls = [...interaction.querySelectorAll('[role="tab"]')];
  const panels = [...interaction.querySelectorAll('[role="tabpanel"]')];
  for (const candidate of controls) {
    const selected = candidate === control;
    candidate.setAttribute("aria-selected", String(selected));
    candidate.tabIndex = selected ? 0 : -1;
  }
  for (const panel of panels) {
    panel.hidden = panel.id !== control.getAttribute("aria-controls");
  }
  control.classList.add("is-visited");
  if (moveFocus) control.focus();
}

function initialiseTabs(interaction) {
  const controls = [...interaction.querySelectorAll('[role="tab"]')];
  if (!controls.length) return;
  for (const [index, control] of controls.entries()) {
    control.addEventListener("click", () => activateTab(interaction, control));
    control.addEventListener("keydown", (event) => {
      const horizontal = !["six_tabs", "sidebar_tabs"].includes(
        interaction.dataset.interaction
      );
      const previousKey = horizontal ? "ArrowLeft" : "ArrowUp";
      const nextKey = horizontal ? "ArrowRight" : "ArrowDown";
      let targetIndex = null;
      if (event.key === previousKey) targetIndex = (index - 1 + controls.length) % controls.length;
      if (event.key === nextKey) targetIndex = (index + 1) % controls.length;
      if (event.key === "Home") targetIndex = 0;
      if (event.key === "End") targetIndex = controls.length - 1;
      if (targetIndex !== null) {
        event.preventDefault();
        activateTab(interaction, controls[targetIndex], true);
      }
    });
  }
  activateTab(interaction, controls.find((item) => item.getAttribute("aria-selected") === "true") || controls[0]);
}

function initialiseAccordion(interaction) {
  const controls = [...interaction.querySelectorAll(".accordion-control")];
  for (const control of controls) {
    control.addEventListener("click", () => {
      const panel = document.getElementById(control.getAttribute("aria-controls"));
      const willOpen = control.getAttribute("aria-expanded") !== "true";
      control.setAttribute("aria-expanded", String(willOpen));
      panel.hidden = !willOpen;
      control.classList.add("is-visited");
    });
  }
}

function initialiseReveal() {
  const button = document.querySelector(".reveal-button");
  const panel = document.getElementById("checking-lens");
  if (!button || !panel) return;
  button.addEventListener("click", () => {
    const willOpen = button.getAttribute("aria-expanded") !== "true";
    button.setAttribute("aria-expanded", String(willOpen));
    button.textContent = willOpen ? "Hide checking lens" : "Reveal a checking lens";
    panel.hidden = !willOpen;
  });
}

async function initialiseStorylineHost() {
  const frame = document.querySelector("[data-story-src]");
  const actions = document.querySelector(".storyline-actions");
  const wrap = document.querySelector(".storyline-frame-wrap");
  const status = document.getElementById("storyline-status");
  if (!frame || !actions || !wrap || !status) return;
  try {
    const response = await fetch("story.html", { method: "HEAD", cache: "no-store" });
    if (!response.ok) return;
    frame.src = frame.dataset.storySrc;
    actions.hidden = false;
    wrap.hidden = false;
    status.textContent = "The complete Storyline Web edition is available below. Use the full-screen link if your browser blocks the embedded player.";
  } catch (_error) {
    // Local file browsing and pre-publish bundles intentionally use the HTML fallback.
  }
}

for (const interaction of document.querySelectorAll(".interaction")) {
  if (interaction.dataset.interaction === "simple_accordion") {
    initialiseAccordion(interaction);
  } else {
    initialiseTabs(interaction);
  }
}
initialiseReveal();
initialiseStorylineHost();

function initialiseCourseMenu() {
  const page = document.querySelector(".course-home");
  const toggle = document.querySelector(".course-menu-toggle");
  const sidebar = document.getElementById("course-sidebar");
  const scrim = document.querySelector("[data-close-menu]");
  if (!page || !toggle || !sidebar || !scrim) return;

  function setMenu(open, returnFocus = false) {
    page.dataset.navOpen = String(open);
    toggle.setAttribute("aria-expanded", String(open));
    scrim.hidden = !open;
    if (open) {
      sidebar.querySelector("a, summary")?.focus();
    } else if (returnFocus) {
      toggle.focus();
    }
  }

  toggle.addEventListener("click", () => {
    setMenu(toggle.getAttribute("aria-expanded") !== "true");
  });
  scrim.addEventListener("click", () => setMenu(false, true));
  sidebar.addEventListener("click", (event) => {
    if (event.target.closest("a") && window.matchMedia("(max-width: 780px)").matches) {
      setMenu(false);
    }
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && toggle.getAttribute("aria-expanded") === "true") {
      setMenu(false, true);
    }
  });
  window.addEventListener("resize", () => {
    if (!window.matchMedia("(max-width: 780px)").matches) setMenu(false);
  });
}

initialiseCourseMenu();
