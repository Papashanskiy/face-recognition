WHITE_NOISE_IMAGE = 'http://25.media.tumblr.com/34976460fad4c39c58c0451bd782b42c/tumblr_mjrexrXM2r1qessyeo1_500.gif';

WIDGET_SCAN_MODE_INITIAL_STATE = '\
    <div class="faces-widget-placeholder__bg"><img class="js-image-one-face" src="'+ WHITE_NOISE_IMAGE +'" width="50" height="50"></div> \
    <div class="faces-widget-placeholder__fg"> \
        <div class="text-right" style="font-size: 12pt; opacity: 0.2; color: white;"><i style="cursor: pointer" class="ti-video-camera"></i></div> \
    </div>\
';

WIDGET_EDIT_MODE_INITIAL_STATE = '<!-- нарисовать -->';


faces_widget = {

    init: function (obj, mode, active_subject_id, active_subject_id_callback, subject_url_template, title_by_subject_id_func) {
        /*
           obj - объект, внутри которого рисуем наш виджет
           mode - режим виджета. Режимы:
              - 'scan' - простой режим, показываем текущие лица, на известное лицо можно кликнуть и перейти на subject_url_template
              - 'subject_edit' - режим редактирования карточки пациента active_subject_id, оператор может сопоставить фотку этому субъекту, мы должны вызвать active_subject_id_callback

           title_by_subject_id_func - js-функция, которая возвращает параметры пациента по его subject_id

           TODO: добавить другие настройки - цвет, расположение и т.п.

        */
        this.obj = $(obj);
        this.mode = mode || 'scan';

        this.active_subject_id = active_subject_id;
        this.active_subject_id_callback = active_subject_id_callback;
        this.subject_url_template = subject_url_template;
        this.title_by_subject_id_func = title_by_subject_id_func;

        this.draw();

        return this;
    },

    reload_background_image: function(){
        /* Перерисовать фон мини-виджета */
        console.debug('reload_background_image start');
        $.getJSON('/faces.json?count=1&filter=recognized&last_seconds=30', function(data){
            console.log('data=', data);
            var face = data.faces[0];
            if(face){
                var id = face['id']; // это id мастер-фотки
                var subject_id = face['subject_id'];
                var master_src =  face['image'];
                var last_seen_src = face.images[0].src;
                var new_src = last_seen_src;
            } else {
                // нет распознанных лиц - покажем что-нибудь
                var id = null;
                var new_src = 'https://media.giphy.com/media/11DuGoDeWBjNAc/giphy.gif';
            };
            $('img.js-image-one-face').each(function(){
                this.src = new_src; // чтобы меньше мелкало - можно показывать master_src
                if(subject_id){
                    $(this).on('click', function () {
                        window.location = '/dashboard/patientcard.html?patient='+subject_id;
                    })
                } else {
                    $(this).off('click');
                }
            })
        }).always(function(){
            console.debug('reload_background_image setTimeout', faces_widget.reload_background_image);
            setTimeout(faces_widget.reload_background_image, 2000);
        }).fail(function(){
            // Покажем шум, если не смогли соединиться с сервером
            $('img.js-image-one-face').each(function(){
                    this.src = WHITE_NOISE_IMAGE;
                });
        })

    },

    draw: function () {
        if(this.mode === 'scan') {
            this.obj.html(WIDGET_SCAN_MODE_INITIAL_STATE);
            // TODO: фотка на бэкграунте должна меняться, прилетать из api
            // TODO: при клике на глаз виджет показывает известных людей

            setTimeout(this.reload_background_image, 2000);

            $('.js-eye').click(function (event) {
                if ($('.js-image').length === 0) {

                    $.getJSON('/faces.json', function(data){
                    var items = [];
                    $.each(data, function(key, value){
                        for (var i = 0; i < Math.min(5, value.length); i++) {
                            var name;
                            if (value[i]['subject_id'] === null) {
                                name = 'no name';
                            } else {
                                name = value[i]['subject_id'];
                            }
                            var id = value[i]['id'];
                            items.push('<td class="images js-image col-lg-3 col-sm-6" id="' + value[i].id + '">' + '<img class="face-image" src="' + value[i].images[0].src +'">' + '<br><div class="image-text-name">' + name + '</div></td>');
                        }
                    });
                    $('<tr>', {
                        'class': 'js-face-table',
                        html: items.join('')
                    }).replaceAll($('.js-face-table'));

                    $('.js-table-images').addClass("table-image");

                    });
                } else {
                    $('.js-table-images').removeClass("table-image");
                    $('.js-image').replaceWith("");
                }

            });


        } else if (this.mode === 'subject_edit') {
            this.obj.html(WIDGET_EDIT_MODE_INITIAL_STATE)
            // TODO: нарисовать начальный виджет для этого режима
            // TODO: думаю, что тут надо показывать 3-5 последних нераспознаных фоток из api
            // TODO: при клике на фото - показывать модальное окно с вопросом "прикрепить фото к этому пациенту?"
            // TODO: ... в случае ответа "да" - отправлять привязку в api и вызывать колбэк active_subject_id_callback
        } else {
            console.error('unknown widget state ', this.mode)
        };

        this.obj.show();

    }


};

