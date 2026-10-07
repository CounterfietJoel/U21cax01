(() => {
  const KEY = 'u21cax01-progress-v1';
  const load = () => { try { return JSON.parse(localStorage.getItem(KEY)) || {}; } catch (e) { return {}; } };
  const save = data => { try { localStorage.setItem(KEY, JSON.stringify(data)); } catch (e) { /* storage unavailable */ } };

  // Multiple-choice sets: first answer counts; explanation always shown.
  document.querySelectorAll('.mcqs').forEach(set => {
    const items = [...set.querySelectorAll('.mcq')];
    const result = set.parentElement.querySelector('.set-result');
    const setId = set.dataset.set;
    const update = () => {
      const answered = items.filter(i => i.dataset.state);
      const right = items.filter(i => i.dataset.state === 'right').length;
      if (!result) return;
      if (answered.length < items.length) {
        result.textContent = answered.length ? `${right} of ${answered.length} correct so far.` : '';
        result.classList.remove('done');
        return;
      }
      const all = right === items.length;
      result.textContent = all
        ? `All ${items.length} correct.${set.closest('.topic') ? ' This topic is marked as revised.' : ''}`
        : `${right} of ${items.length} correct. Re-read the explanations and the topic, then try again tomorrow.`;
      result.classList.toggle('done', all);
      const data = load();
      if (set.closest('.topic') && all) { data[setId] = Date.now(); save(data); }
      if (!set.closest('.topic')) { data[`quiz:${setId}`] = { right, total: items.length, at: Date.now() }; save(data); }
    };
    items.forEach(item => {
      const opts = [...item.querySelectorAll('.opt')];
      opts.forEach(opt => opt.addEventListener('click', () => {
        if (item.dataset.state) return;
        const correct = opt.dataset.correct === 'true';
        item.dataset.state = correct ? 'right' : 'wrong';
        item.classList.add(correct ? 'answered-right' : 'answered-wrong');
        opts.forEach(o => {
          o.disabled = true;
          if (o.dataset.correct === 'true') o.classList.add('is-right');
        });
        if (!correct) opt.classList.add('is-wrong');
        const fb = item.querySelector('.feedback');
        fb.querySelector('.verdict').textContent = correct ? 'Correct.' : 'Not quite.';
        fb.hidden = false;
        update();
      }));
    });
    const reset = set.parentElement.querySelector('.reset');
    if (reset) reset.addEventListener('click', () => {
      items.forEach(item => {
        delete item.dataset.state;
        item.classList.remove('answered-right', 'answered-wrong');
        item.querySelectorAll('.opt').forEach(o => { o.disabled = false; o.classList.remove('is-right', 'is-wrong'); });
        item.querySelector('.feedback').hidden = true;
      });
      update();
      set.querySelector('.opt')?.focus();
    });
  });

  // Flashcards.
  document.querySelectorAll('.flash').forEach(card => card.addEventListener('click', () => {
    card.setAttribute('aria-pressed', String(card.getAttribute('aria-pressed') !== 'true'));
  }));

  // Progress ticks on hub and home.
  const data = load();
  document.querySelectorAll('[data-progress]').forEach(link => {
    if (data[link.dataset.progress]) { link.classList.add('is-done'); link.setAttribute('title', 'Quick check completed'); }
  });
  document.querySelectorAll('[data-unit-count]').forEach(el => {
    const list = document.querySelectorAll('.topic-list [data-progress]');
    el.textContent = [...list].filter(l => data[l.dataset.progress]).length;
  });
})();
