(function(){
    $(document).ready(function(){
        $.when(get_tacos()).then(
            function(taco){
                var main_title = taco.base_layer.name + ' <strong>with</strong> ' + taco.mixin.name + ', <strong>garnished with</strong> ' + taco.condiment.name + ' <strong>and topped off with</strong> ' + taco.seasoning.name;
                document.title = taco.base_layer.name + ' | ' + taco.mixin.name + ' | ' + taco.condiment.name + ' | ' + taco.seasoning.name;
                $('#taco-content').append('<h1 class="light">' + main_title + '</h1>');
                var permalink = '/' + taco.base_layer.slug + '/';
                permalink += taco.mixin.slug + '/';
                permalink += taco.condiment.slug + '/';
                permalink += taco.seasoning.slug + '/';
                $('#taco-content').append('<a href="' + permalink + '"><h5 class="light">Permalink to this taco</a></h5><hr/>')
                var renderer = new EJS({url: '/static/js/views/taco.ejs'});
                $('#taco-content').append(renderer.render(taco));
            }
        )
    });
    function get_tacos(){
        return $.ajax({
            url: '/random/',
            type: 'GET',
            dataType: 'json'
        })
    }
})()
