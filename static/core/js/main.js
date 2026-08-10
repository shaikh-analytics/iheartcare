(function ($) {
    "use strict";
    
    // Dropdown on mouse hover
    $(document).ready(function () {
        function toggleNavbarMethod() {
            if ($(window).width() > 992) {
                $('.navbar .dropdown').on('mouseover', function () {
                    $('.dropdown-toggle', this).trigger('click');
                }).on('mouseout', function () {
                    $('.dropdown-toggle', this).trigger('click').blur();
                });
            } else {
                $('.navbar .dropdown').off('mouseover').off('mouseout');
            }
        }
        toggleNavbarMethod();
        $(window).resize(toggleNavbarMethod);
    });


    // Shrink navbar on scroll
    function toggleNavbarScrolled() {
        if ($(window).scrollTop() > 50) {
            $('#mainNavbar').addClass('nav-scrolled');
        } else {
            $('#mainNavbar').removeClass('nav-scrolled');
        }
    }
    toggleNavbarScrolled();
    $(window).scroll(toggleNavbarScrolled);


    // Date and time picker
    $('.date').datetimepicker({
        format: 'L'
    });
    $('.time').datetimepicker({
        format: 'LT'
    });


    // Appointment form - filter doctors by selected department
    var $doctorSelect = $('#id_doctor');
    if ($doctorSelect.length) {
        var $allDoctorOptions = $doctorSelect.find('option').clone();

        function filterDoctorsByDepartment(departmentId) {
            var currentValue = $doctorSelect.val();
            $doctorSelect.empty();
            $allDoctorOptions.each(function () {
                var $opt = $(this);
                var deptIds = ($opt.attr('data-department') || '').split(' ');
                if (!$opt.val() || !departmentId || deptIds.indexOf(departmentId) !== -1) {
                    $doctorSelect.append($opt.clone());
                }
            });
            if ($doctorSelect.find('option[value="' + currentValue + '"]').length) {
                $doctorSelect.val(currentValue);
            } else {
                $doctorSelect.val('');
            }
        }

        $(document).on('change', '#id_department', function () {
            filterDoctorsByDepartment($(this).val());
        });

        filterDoctorsByDepartment($('#id_department').val());
    }
    
    
    // Back to top button
    $(window).scroll(function () {
        if ($(this).scrollTop() > 100) {
            $('.back-to-top').fadeIn('slow');
        } else {
            $('.back-to-top').fadeOut('slow');
        }
    });
    $('.back-to-top').click(function () {
        $('html, body').animate({scrollTop: 0}, 1500, 'easeInOutExpo');
        return false;
    });


    // Hero banner carousel
    $(".hero-carousel").owlCarousel({
        autoplay: true,
        autoplayTimeout: 5000,
        smartSpeed: 1000,
        items: 1,
        dots: true,
        loop: true,
        nav : true,
        navText : [
            '<i class="bi bi-arrow-left"></i>',
            '<i class="bi bi-arrow-right"></i>'
        ],
    });


    // Our Doctors carousel
    $(".doctors-carousel").owlCarousel({
        autoplay: true,
        smartSpeed: 1000,
        margin: 45,
        dots: false,
        loop: true,
        nav : true,
        navText : [
            '<i class="bi bi-arrow-left"></i>',
            '<i class="bi bi-arrow-right"></i>'
        ],
        responsive: {
            0:{
                items:1
            },
            992:{
                items:2
            },
            1200:{
                items:3
            }
        }
    });


    // Team carousel
    $(".team-carousel, .related-carousel").owlCarousel({
        autoplay: true,
        smartSpeed: 1000,
        margin: 45,
        dots: false,
        loop: true,
        nav : true,
        navText : [
            '<i class="bi bi-arrow-left"></i>',
            '<i class="bi bi-arrow-right"></i>'
        ],
        responsive: {
            0:{
                items:1
            },
            992:{
                items:2
            }
        }
    });


    // Testimonials carousel
    $(".testimonial-carousel").owlCarousel({
        autoplay: true,
        smartSpeed: 1000,
        items: 1,
        dots: true,
        loop: true,
    });


    // Find A Doctor - live autocomplete suggestions
    var doctorSearchTimer = null;
    var doctorSearchXhr = null;
    var activeSuggestionIndex = -1;

    function escapeHtml(text) {
        return $('<div>').text(text || '').html();
    }

    function renderSuggestions($box, results) {
        $box.empty();
        activeSuggestionIndex = -1;

        if (!results.length) {
            $box.append('<div class="doctor-search-empty">No doctors found</div>');
            $box.addClass('show');
            return;
        }

        results.forEach(function (doctor) {
            var meta = [doctor.designation, doctor.department].filter(Boolean).join(' &middot; ');
            var $item = $(
                '<a class="doctor-search-suggestion" href="' + doctor.url + '">' +
                    '<img src="' + doctor.photo + '" alt="' + escapeHtml(doctor.name) + '">' +
                    '<span>' +
                        '<span class="d-block">' + escapeHtml(doctor.name) + '</span>' +
                        (meta ? '<span class="suggestion-meta">' + meta + '</span>' : '') +
                    '</span>' +
                '</a>'
            );
            $box.append($item);
        });
        $box.addClass('show');
    }

    $(document).on('input', '.doctor-search-input', function () {
        var $input = $(this);
        var $form = $input.closest('.doctor-search-form');
        var $box = $form.find('.doctor-search-suggestions');
        var query = $input.val().trim();
        var suggestUrl = $form.data('suggest-url');

        clearTimeout(doctorSearchTimer);

        if (!query) {
            $box.removeClass('show').empty();
            return;
        }

        doctorSearchTimer = setTimeout(function () {
            if (doctorSearchXhr) {
                doctorSearchXhr.abort();
            }
            doctorSearchXhr = $.getJSON(suggestUrl, { q: query })
                .done(function (data) {
                    renderSuggestions($box, data.results || []);
                });
        }, 250);
    });

    // Keyboard navigation through suggestions
    $(document).on('keydown', '.doctor-search-input', function (e) {
        var $form = $(this).closest('.doctor-search-form');
        var $box = $form.find('.doctor-search-suggestions');
        var $items = $box.find('.doctor-search-suggestion');

        if (!$box.hasClass('show') || !$items.length) {
            return;
        }

        if (e.key === 'ArrowDown') {
            e.preventDefault();
            activeSuggestionIndex = Math.min(activeSuggestionIndex + 1, $items.length - 1);
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            activeSuggestionIndex = Math.max(activeSuggestionIndex - 1, 0);
        } else if (e.key === 'Enter' && activeSuggestionIndex > -1) {
            e.preventDefault();
            window.location.href = $items.eq(activeSuggestionIndex).attr('href');
            return;
        } else if (e.key === 'Escape') {
            $box.removeClass('show');
            return;
        } else {
            return;
        }

        $items.removeClass('active');
        $items.eq(activeSuggestionIndex).addClass('active');
    });

    // Hide suggestions when clicking outside the search box
    $(document).on('click', function (e) {
        if (!$(e.target).closest('.doctor-search-form').length) {
            $('.doctor-search-suggestions').removeClass('show');
        }
    });

    // Re-show suggestions on refocus if there's already a query with results
    $(document).on('focus', '.doctor-search-input', function () {
        var $box = $(this).closest('.doctor-search-form').find('.doctor-search-suggestions');
        if ($box.children().length) {
            $box.addClass('show');
        }
    });

})(jQuery);

