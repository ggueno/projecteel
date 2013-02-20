
var searchEngine = {
    search_url : "",
    search_datas : "",
    container : "",

    init : function(container){
        this.search_url = $(".search-form").attr('action');
        this.search_datas = new Array();
        this.container = container;

        //foreach search-field
        var that = this;

        // Parcourir le DOM pour trouver des champs
        $('.search-field').each(function(index){
            var title = $(this).attr('id').replace('search-','');
            if( $(this).hasClass('autocomplete') ){

                $(this).autoSuggest("/list/"+title+"/",
                {
                    minChars: 2,
                    matchCase: false,
                    startText: title,
                    resultClick: function(elem){ that.addToSearch(title, elem.attributes.name, false); return elem;  },
                    selectionAdded: function(elem){ return elem;},
                    selectionRemoved: function(elem){
                        var id = $(elem).parent().attr('id').replace('as-selections-','');
                        console.log($("#as-input-"+id).attr('name'));
                        that.removeFromSearch(title, $(elem).data('value'));
                        $(elem).remove();
                    }
                });
                that.search_datas[title] = new Array();
            }

            else if( $(this).is('select') ){
                $('#search-'+title).change(function(){
                    that.addToSearch(title, $(this).val(), true);
                    return false;
                });

                that.search_datas[title] = $(this).val();
            }

            else if( $(this).hasClass('dropdown')){
                $(this).find('ul a').click(function(e){

                    e.preventDefault();

                    that.addToSearch(title, $(this).data('value'), true);

                    // var toogle = $(this).parent().parent().parent().find('.dropdown-toggle');
                    // var value = $(toogle).data('value');
                    // var title = $(toogle).html();

                    // console.log(toogle);

                    // $(toogle).data('value',$(this).data('value'));
                    // $(toogle).html($(this).html());

                    // $(this).data('value', value);
                    // $(this).html(title);

                    return true;
                });
            }

            else if( $(this).is('input') ){
                $(this).keypress(function(e) {
                    
                    if(e.which == 13) {
                        that.addToSearch(title,$(this).val(), true);
                        return true;
                    }
                });



                that.search_datas[title] = new Array();
            }
        });




         $('#search-durationmin').keypress(function(e){
            if(e.which == 13){
                that.addToSearch('durationmin', $(this).val(), true);
                return false;
            }
         });


         $('#search-durationmax').keypress(function(e){
            if(e.which == 13){
                that.addToSearch('durationmax', $(this).val(), true)
                return false;
            }
         });



        this.search_datas['durationmin'] = -1;
        this.search_datas['durationmax'] = -1;



        $('.project-search').submit(function(){ return false; });
    },

    addField : function () {},
    removeField : function() {},


    addToSearch : function(type, val, unique){
        if(unique){
            this.search_datas[type] = val;
        }else{
            this.search_datas[type].push(val);
        }
        this.sendSearch();
    },

    removeFromSearch : function(type, val, unique){
        if(unique){
            this.search_datas[type].splice(val);
        }else{
            this.search_datas[type] = new Array();
        }
        this.sendSearch();
    },

    sendSearch : function(){

        var datas = new Object();
        for(key in this.search_datas) {
            if(this.search_datas[key] != -1){
                if(this.search_datas[key] instanceof Array){
                    datas[key+'[]'] = this.search_datas[key];
                }else{
                    datas[key] = this.search_datas[key];
                }
            }
        }

        var that = this;

        $.ajax({
            type: "GET",
            url : this.search_url,

            traditional: true,
            data : datas,
            success:
                function(result, status){
                    $(that.container).html(result);
                },
        });
    }
}