/**
 * Custom Select Component
 * Replaces native <select> elements with a styled dropdown
 */

document.addEventListener('DOMContentLoaded', function() {
    // Find all forms with custom-select elements
    const forms = document.querySelectorAll('.preference-form');

    forms.forEach(form => {
        initCustomSelects(form);
    });
});

function initCustomSelects(form) {
    // Find all select elements within the form
    const selects = form.querySelectorAll('select');

    selects.forEach(select => {
        // Create custom select wrapper
        const wrapper = document.createElement('div');
        wrapper.className = 'custom-select';
        wrapper.setAttribute('data-name', select.name);

        // Get selected option
        const selectedOption = select.options[select.selectedIndex];
        const selectedValue = selectedOption.value;
        const selectedText = selectedOption.text;

        // Create trigger (visible part)
        const trigger = document.createElement('div');
        trigger.className = 'custom-select-trigger';
        trigger.innerHTML = `
            <span class="select-value">${selectedText}</span>
            <svg class="select-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="6 9 12 15 18 9"></polyline>
            </svg>
        `;

        // Create hidden native select (for form submission)
        const nativeSelect = document.createElement('select');
        nativeSelect.className = 'custom-select-native';
        nativeSelect.name = select.name;
        nativeSelect.required = select.required;

        // Copy all options to native select
        Array.from(select.options).forEach((opt, idx) => {
            const option = document.createElement('option');
            option.value = opt.value;
            option.text = opt.text;
            option.selected = idx === select.selectedIndex;
            nativeSelect.appendChild(option);
        });

        // Create dropdown
        const dropdown = document.createElement('div');
        dropdown.className = 'custom-select-dropdown';

        // Add options
        Array.from(select.options).forEach((opt, idx) => {
            const optionEl = document.createElement('div');
            optionEl.className = 'custom-select-option';
            if (idx === select.selectedIndex) {
                optionEl.classList.add('selected');
            }
            optionEl.innerHTML = `<span class="option-label">${opt.text}</span>`;
            optionEl.setAttribute('data-value', opt.value);

            optionEl.addEventListener('click', () => {
                // Update selected state
                dropdown.querySelectorAll('.custom-select-option').forEach(o => o.classList.remove('selected'));
                optionEl.classList.add('selected');

                // Update trigger text
                trigger.querySelector('.select-value').textContent = opt.text;

                // Update native select
                nativeSelect.value = opt.value;

                // Close dropdown
                closeDropdown();
            });

            dropdown.appendChild(optionEl);
        });

        // Toggle dropdown on trigger click
        trigger.addEventListener('click', (e) => {
            e.stopPropagation();
            const isOpen = trigger.classList.contains('open');

            // Close all other dropdowns first
            document.querySelectorAll('.custom-select-trigger.open').forEach(t => {
                t.classList.remove('open');
                t.parentElement.querySelector('.custom-select-dropdown').classList.remove('open');
            });

            if (!isOpen) {
                trigger.classList.add('open');
                dropdown.classList.add('open');
            }
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!wrapper.contains(e.target)) {
                closeDropdown();
            }
        });

        function closeDropdown() {
            trigger.classList.remove('open');
            dropdown.classList.remove('open');
        }

        // Replace original select
        wrapper.appendChild(trigger);
        wrapper.appendChild(nativeSelect);
        wrapper.appendChild(dropdown);

        select.parentNode.replaceChild(wrapper, select);
    });
}
