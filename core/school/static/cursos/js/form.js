document.addEventListener('DOMContentLoaded', function (e) {
    const form = document.getElementById('frmForm');
    FormValidation.validators.checkMinCoupon = verifyMinCoupon;
    const fv = FormValidation.formValidation(form, {
            locale: 'es_ES',
            localization: FormValidation.locales.es_ES,
            plugins: {
                trigger: new FormValidation.plugins.Trigger(),
                submitButton: new FormValidation.plugins.SubmitButton(),
                bootstrap: new FormValidation.plugins.Bootstrap(),
                icon: new FormValidation.plugins.Icon({
                    valid: 'fa fa-check',
                    invalid: 'fa fa-times',
                    validating: 'fa fa-refresh',
                }),
            },
            fields: {
                name: {
                    validators: {
                        notEmpty: {},
                        stringLength: {
                            min: 2,
                        },
                        remote: {
                            url: pathname,
                            data: function () {
                                return {
                                    obj: form.querySelector('[name="name"]').value,
                                    type: 'name',
                                    action: 'validate_data'
                                };
                            },
                            message: 'El nombre del nivel ya se encuentra registrado',
                            method: 'POST'
                        }
                    }
                },
                max_coupon: {
                    validators: {
                        stringLength: {
                            min: 1,
                        },
                        notEmpty: {
                            message: 'Campo obligatorio',
                        },
                    }
                },
                min_coupon: {
                    validators: {
                        stringLength: {
                            min: 1,
                        },
                        notEmpty: {
                            message: 'Campo obligatorio',
                        },
                        checkMinCoupon: {
                            message: "El cupo mínimo debe ser menor que el cupo máximo"
                        }
                    }
                },
                
            },
        }
        
    )
        .on('core.element.validated', function (e) {
            if (e.valid) {
                const groupEle = FormValidation.utils.closest(e.element, '.form-group');
                if (groupEle) {
                    FormValidation.utils.classSet(groupEle, {
                        'has-success': false,
                    });
                }
                FormValidation.utils.classSet(e.element, {
                    'is-valid': false,
                });
            }
            const iconPlugin = fv.getPlugin('icon');
            const iconElement = iconPlugin && iconPlugin.icons.has(e.element) ? iconPlugin.icons.get(e.element) : null;
            iconElement && (iconElement.style.display = 'none');
        })
        .on('core.validator.validated', function (e) {
            if (!e.result.valid) {
                const messages = [].slice.call(form.querySelectorAll('[data-field="' + e.field + '"][data-validator]'));
                messages.forEach((messageEle) => {
                    const validator = messageEle.getAttribute('data-validator');
                    messageEle.style.display = validator === e.validator ? 'block' : 'none';
                });
            }
        })
        .on('core.form.valid', function () {
            submit_formdata_with_ajax_form(fv);
        });
});

$(function () {
    $('input[name="name"]').keypress(function (e) {
        return validate_form_text('number', e, null);
    });
});


const verifyMinCoupon = () => {
    return {
        validate: (input) => {
            const value = input.value;
            const max_coupon =  document.getElementById('id_max_coupon').value;

            if (Number(value) > Number(max_coupon)) {
                return { valid: false };
            }

            return { valid: true };
        },
    };
};

