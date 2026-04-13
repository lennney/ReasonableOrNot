/**
 * Custom Select Component
 * Replaces native <select> elements with a styled dropdown
 * Includes accessibility: ARIA attributes, keyboard navigation
 */

const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('.preference-form');
    forms.forEach(form => {
        initCustomSelects(form);
    });
});

function initCustomSelects(form) {
    const selects = form.querySelectorAll('select');

    selects.forEach(select => {
        const wrapper = document.createElement('div');
        wrapper.className = 'custom-select';
        wrapper.setAttribute('data-name', select.name);

        const selectId = select.id || `select-${select.name}`;
        const label = form.querySelector(`label[for="${selectId}"]`);
        const labelText = label ? label.textContent.trim() : select.name;

        const selectedOption = select.options[select.selectedIndex];
        const selectedText = selectedOption ? selectedOption.text : '';

        // Create trigger with ARIA
        const trigger = document.createElement('div');
        trigger.className = 'custom-select-trigger';
        trigger.setAttribute('role', 'combobox');
        trigger.setAttribute('aria-expanded', 'false');
        trigger.setAttribute('aria-haspopup', 'listbox');
        trigger.setAttribute('aria-labelledby', selectId);
        trigger.setAttribute('tabindex', '0');
        trigger.innerHTML = `
            <span class="select-value">${selectedText}</span>
            <svg class="select-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
                <polyline points="6 9 12 15 18 9"></polyline>
            </svg>
        `;

        // Hidden native select for form submission
        const nativeSelect = document.createElement('select');
        nativeSelect.className = 'custom-select-native';
        nativeSelect.name = select.name;
        nativeSelect.required = select.required;
        nativeSelect.id = selectId;

        Array.from(select.options).forEach((opt, idx) => {
            const option = document.createElement('option');
            option.value = opt.value;
            option.text = opt.text;
            option.selected = idx === select.selectedIndex;
            nativeSelect.appendChild(option);
        });

        // Create dropdown with ARIA
        const dropdown = document.createElement('div');
        dropdown.className = 'custom-select-dropdown';
        if (prefersReducedMotion) {
            dropdown.style.animation = 'none';
        }
        dropdown.setAttribute('role', 'listbox');
        dropdown.setAttribute('aria-label', labelText);

        // Add options
        const optionEls = [];
        Array.from(select.options).forEach((opt, idx) => {
            const optionEl = document.createElement('div');
            optionEl.className = 'custom-select-option';
            optionEl.setAttribute('role', 'option');
            optionEl.setAttribute('data-value', opt.value);
            optionEl.setAttribute('tabindex', '-1');

            if (idx === select.selectedIndex) {
                optionEl.classList.add('selected');
                optionEl.setAttribute('aria-selected', 'true');
            } else {
                optionEl.setAttribute('aria-selected', 'false');
            }

            optionEl.innerHTML = `<span class="option-label">${opt.text}</span>`;

            optionEl.addEventListener('click', () => {
                selectOption(optionEl, opt.text, opt.value, dropdown, trigger);
            });

            dropdown.appendChild(optionEl);
            optionEls.push(optionEl);
        });

        // Keyboard navigation
        trigger.addEventListener('keydown', (e) => {
            const isOpen = trigger.classList.contains('open');

            switch (e.key) {
                case 'Enter':
                case ' ':
                    e.preventDefault();
                    if (isOpen) {
                        closeDropdown();
                    } else {
                        openDropdown();
                    }
                    break;
                case 'ArrowDown':
                    e.preventDefault();
                    if (!isOpen) openDropdown();
                    navigateOptions(1);
                    break;
                case 'ArrowUp':
                    e.preventDefault();
                    if (!isOpen) openDropdown();
                    navigateOptions(-1);
                    break;
                case 'Escape':
                    if (isOpen) {
                        e.preventDefault();
                        closeDropdown();
                        trigger.focus();
                    }
                    break;
                case 'Tab':
                    if (isOpen) closeDropdown();
                    break;
            }
        });

        dropdown.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                closeDropdown();
                trigger.focus();
            }
        });

        function navigateOptions(direction) {
            const current = dropdown.querySelector('.selected');
            const options = dropdown.querySelectorAll('.custom-select-option');
            let idx = Array.from(options).indexOf(current);
            idx = (idx + direction + options.length) % options.length;
            selectOption(options[idx], options[idx].textContent, options[idx].dataset.value, dropdown, trigger);
            options[idx].focus();
        }

        function openDropdown() {
            trigger.classList.add('open');
            dropdown.classList.add('open');
            trigger.setAttribute('aria-expanded', 'true');
        }

        function closeDropdown() {
            trigger.classList.remove('open');
            dropdown.classList.remove('open');
            trigger.setAttribute('aria-expanded', 'false');
        }

        function selectOption(optionEl, text, value, dropdown, trigger) {
            dropdown.querySelectorAll('.custom-select-option').forEach(o => {
                o.classList.remove('selected');
                o.setAttribute('aria-selected', 'false');
            });
            optionEl.classList.add('selected');
            optionEl.setAttribute('aria-selected', 'true');

            trigger.querySelector('.select-value').textContent = text;
            nativeSelect.value = value;

            closeDropdown();
            trigger.focus();
        }

        // Click outside to close
        document.addEventListener('click', (e) => {
            if (!wrapper.contains(e.target)) {
                closeDropdown();
            }
        });

        trigger.addEventListener('click', (e) => {
            e.stopPropagation();
            if (trigger.classList.contains('open')) {
                closeDropdown();
            } else {
                openDropdown();
            }
        });

        wrapper.appendChild(trigger);
        wrapper.appendChild(nativeSelect);
        wrapper.appendChild(dropdown);

        select.parentNode.replaceChild(wrapper, select);
    });
}
