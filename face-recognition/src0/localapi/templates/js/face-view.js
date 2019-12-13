$(document).ready(function() {
    function updateFaceTable() {
        $.getJSON('/faces.json', function(data){
            // console.dir(data);
            var items = [];
            $.each(data, function(key, value){
                // console.dir(value);
                for (var i = 0; i < Math.min(5, value.length); i++) {
                    var name;
                    if (value[i]['subject_id'] === null) {
                        name = 'no name';
                    } else {
                        name = value[i]['subject_id'];
                    }
                    var id = value[i]['id'];
                    items.push('<td class="images js-image" id="' + value[i].id + '">' + '<img class="face-image" src="' + value[i].images[0].src + '"><br><div class="image-text-name">' + name + ' <a href="/face-edit.html?id=' + id + '">edit</a>' + '</div>' + '</td>');
                }
            });
            if ($('.js-face-table').length > 0) {
                $('<tr>', {
                    'class': 'js-face-table',
                    html: items.join('')
                }).replaceAll($('.js-face-table'));
            } else {
                $('<tr>', {
                    'class': 'js-face-table',
                    html: items.join('')
                }).appendTo("table");
            }
        });
    }
    var client;
    $('.js-client').click(function (event) {
        if ($('.js-client').hasClass("select")) {
            if (($(event.currentTarget).hasClass("select"))) {
                $(event.currentTarget).removeClass("select");
                $(".js-client-card").addClass("hide");
                $(".js-search").removeClass("hide");
                $(event.currentTarget).removeClass("main-card");
                $('.js-client').removeClass("hide");;

            } else {
                $(".js-client").removeClass("select");
                $(event.currentTarget).addClass("select");
                $(event.currentTarget).removeClass("hide");
                $(".js-search").addClass("hide");
                $(".js-client").removeClass("main-card");
                $(event.currentTarget).addClass("main-card");
                $('.js-client-card').addClass("hide");
                $('.js-client').addClass("hide");
                $(event.currentTarget).removeClass("hide");
                $(event.currentTarget).next().removeClass("hide");
            }
        }
        else {
            $(event.currentTarget).addClass("select");
            $(".js-client-card").removeClass("hide");
            $(".js-search").addClass("hide");
            $(event.currentTarget).addClass("main-card");
            $('.js-client-card').addClass("hide");
            $('.js-client').addClass("hide");
            $(event.currentTarget).removeClass("hide");
            $(event.currentTarget).next().removeClass("hide");
            $(".js-back").removeClass("hide");
        }
        client = $(event.currentTarget).find(".select").text;
    });
    $(document).on('click', '.js-image', function (event) {
        if ($('.js-client').hasClass("select")) {
            var name = $('.js-choose-clients').find(".select").text();
            var id = $(event.currentTarget).attr('id');
            $.ajax({
                type: 'POST',
                url: '/face-link',
                data: {
                    'id': id,
                    'subject_id': name
                },
                success: function () {
                    $('.js-client').removeClass("select");
                    updateFaceTable();
                }
            });
        }
    });
    updateFaceTable();
    setInterval(updateFaceTable, 4000);
});
