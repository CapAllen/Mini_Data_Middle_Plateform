// $(function() {
//     //点击搜索，把sort,del,update信息都设为none
//     // $('#search').bind('click', function() {
//     //     expo_name = $('input[name="ExpoName"]').val();
//     //     start_date = $('input[name="StartDate"]').val();
//     //     city_name = $('input[name="CityName"]').val();
//     //     sid = $('input[name="Sid"]').val();
//     //     itemid = $('input[name="Itemid"]').val();
//     //     unit_name = $('input[name="UnitName"]').val();
//     //     unit_code = $('input[name="UnitCode"]').val();
//     //     $("#search_info").val(expo_name + '&' + start_date + '&' + city_name + '&' + sid + '&' + itemid + '&' + unit_name + '&' + unit_code); //为排序信息输入框赋值，以便后续翻页时取得该值
//     //     $("#update_info").val('none');
//     //     $("#del_info").val('none');
//     //     $("#sort_info").val('none');
//     //     $("#add_info").val('none');
//     //     show();
//     //     return false;
//     // });


//     /*点击排序,把search,del,update信息都设为none
//      排序有三种状态：无序，升序，降序，默认为无序，第一次点击为升序，第二次点击为降序，第三次点击为无序*/
//     $('th>a').bind('click', function() {
//         sort = $(this).attr('sort'); //首先取出上次的排序方式
//         //alert(sort);
//         if (sort == '') {
//             $(this).attr('sort', 'asc');
//             $(this).next().attr('class', "datagrid-sort-asc");
//         }
//         if (sort == 'asc') {
//             $(this).attr('sort', 'desc');
//             $(this).next().attr('class', "datagrid-sort-desc");
//         }
//         if (sort == 'desc') {
//             $(this).attr('sort', '');
//             $(this).next().attr('class', "datagrid-sort");
//         }
//         sort = $(this).attr('sort');
//         //alert(sort);
//         if (sort != '') {
//             //alert(sort);
//             keyword = $(this).attr('name');
//             //alert(sort+keyword);
//             $("#sort_info").val(keyword + '&' + sort); //为排序信息输入框赋值，以便后续翻页时取得该值
//             $("#update_info").val('none');
//             $("#del_info").val('none');
//             $("#search_info").val('none');
//             $("#add_info").val('none');
//             show();
//         } else {
//             $("#sort_info").val('none');
//         }
//     });

//     //页面加载时调用show()获取数据，此时搜索关键字全为空，所以后台返回全部数据
//     show();

//     //更新操作，input change事件，注册为document（也可以注册为table的事件）的事件是防止表格不存在，因为因为表格是动态生成的
//     $('#event-info').on('change', "td>input", function() {
//         $(this).css("background-color", "#FFFFCC");
//         id = $(this).attr('id');
//         var value = document.getElementById(id).value;
//         //alert(id+value);
//         $("#update_info").val(id + '&' + value); //为修改信息输入框赋值，以便后续翻页时取得该值
//         $("#del_info").val('none');
//         $("#add_info").val('none');
//         current_page = $('#current_page').val();
//         //alert(current_page);
//         show(current_page);
//     });

//     //点击删除
//     $(document).on('click', "tbody td>a", function() {
//         //$('td a').bind('click', function(){
//         id = $(this).attr('id'); //被删除数据的id
//         alert(id);
//         $("#del_info").val(id); //为删除信息输入框赋值
//         $("#update_info").val('none');
//         $("#add_info").val('none');
//         //alert($("#sort_info").val());
//         current_page = $('#current_page').val();
//         show(current_page);
//     });

//     //添加一行
//     $('#addRow').bind('click', function() {
//         addRow();
//     });

//     $(document).on('click', "#addSure", function() {
//         //$('td a').bind('click', function(){
//         itemid = $('input[name="addItemid"]').val();
//         sid = $('input[name="addSid"]').val();
//         expo_name = $('input[name="addExpoName"]').val();
//         start_date = $('input[name="addStartDate"]').val();
//         end_date = $('input[name="addEndDate"]').val();
//         city_name = $('input[name="addCityName"]').val();
//         unit_name = $('input[name="addUnitName"]').val();
//         unit_code = $('input[name="addUnitCode"]').val();
//         site = $('input[name="addSite"]').val();
//         exhibitor = $('input[name="addExhibitor"]').val();
//         visitor = $('input[name="addVisitor"]').val();
//         expo_area = $('input[name="addExpoArea"]').val();
//         get_date = $('input[name="addGetDate"]').val();
//         $("#add_info").val(itemid + '&' + sid + '&' + expo_name + '&' + unit_code + '&' + unit_name + '&' + city_name + '&' + start_date + '&' + end_date + '&' + site + '&' + exhibitor + '&' + visitor + '&' + expo_area + '&' + get_date); //为排序信息输入框赋值，以便后续翻页时取得该值
//         alert($("#add_info").val());
//         $("#update_info").val('none');
//         $("#del_info").val('none');
//         current_page = $('#current_page').val();
//         show(current_page);
//     });

//     //根据复选框状态进行删除
//     $('#mutiple_del').bind('click', function() {
//         var ids = "";
//         $('input[type="checkbox"][name="select"]:checked').each(function() {
//             ids = ids + "&" + $(this).val();
//             $(this).css("background-color", "#FFFFCC");
//         });
//         ids = ids.substring(1, ids.Length);
//         if (ids) {
//             alert(ids);
//             //$("#del_info").attr("value",ids);
//             $("#del_info").val(ids);
//             $("#update_info").val('none');
//             //$("#search_info").val();
//             current_page = $('#current_page').val();
//             show(current_page);
//         } else {
//             alert('请至少选择一项！');
//             return false;
//         }
//     });

//     //选中行变色
//     $('#event-info').on('change', "td>span>input", function() {
//         $(this).parent().parent().parent().toggleClass("tr_select");
//     });


//     //提交所有参数到后台，后台根据参数状态选择对应的操作
//     function show(page) {
//         $.ajax({
//             type: 'GET',
//             url: '/getargs',
//             data: {
//                 Page: page,
//                 SearchInfo: $("#search_info").val(), //包括expo_name,start_date,city_name,sid,itemid,unit_name,unit_code
//                 SortInfo: $("#sort_info").val(), //包括keyword，sort
//                 UpdateInfo: $("#update_info").val(), //包括id，keyword，value
//                 DelInfo: $("#del_info").val(), //包括id
//                 AddInfo: $("#add_info").val() //包括包括itemid,sid,expo_name,unit_code,unit_name,unit_name_en,start_date,end_date,city_name,organizer,site,exhibitor,visitor,expo_area,get_date
//             },
//             success: function(data) {
//                 //alert('success');
//                 events = data.result.splice(1); //result的第一项是页数信息，从第二项开始才是event数据
//                 pagination = data.result[0];
//                 total_num = pagination.total_num;
//                 num = pagination.num;
//                 total_pages = pagination.total_pages;
//                 current_page = pagination.current_page;
//                 $("#current_page").val(current_page);
//                 var $table = $('#event-info');
//                 $table.empty();
//                 createTable(events); //创建表格
//                 createPage(total_pages, current_page); //创建分页
//                 showNum(total_num, num);
//                 showColumn();
//             }
//         });
//     }

//     //显示数据总条数和符合查询条件的条数
//     function showNum(totalNum, num) {
//         $("#showNum").html('总数量' + totalNum + ',符合查询条件的数量' + num);
//     }

//     //创建分页
//     function createPage(count, index) {
//         $("[id*='paginate']").paginate({
//             count: count,
//             start: index,
//             display: 9,
//             border: true,
//             border_color: '#fff',
//             text_color: '#fff',
//             background_color: 'black',
//             border_hover_color: '#ccc',
//             text_hover_color: '#000',
//             background_hover_color: '#fff',
//             images: false,
//             mouse: 'press',
//             onChange: function(page) {
//                 //$('._current', '#paginationdemo').removeClass('_current').hide();
//                 //$('#p' + page).addClass('_current').show();
//                 show(page);
//             }
//         });
//     }


//     //创建表格
//     function createTable(data) {
//         for (i in data) {
//             //for (var i=1;i<data.length;i++)
//             $('#event-info').append(
//                 "<tr>" +
//                 "<td><span><input type='checkbox' name='select' id='select' value=" + data[i].ID + "></span></td>" +
//                 "<td>" + i + "</td>" +
//                 "<input type='hidden' name='id' value=" + data[i].ID + ">" +
//                 "<td>" + "<input " + "id=" + data[i].ID + "&Itemid" + " value=" + data[i].Itemid + ">" + "</td>" +
//                 "<td>" + "<input " + "id=" + data[i].ID + "&Sid" + " value=" + data[i].Sid + ">" + "</td>" +
//                 "<td>" + "<input " + "id=" + data[i].ID + "&ExpoName" + " value='" + data[i].ExpoName + "'>" + "</td>" +
//                 "<td>" + "<input " + "id=" + data[i].ID + "&UnitCode" + " value=" + data[i].UnitCode + ">" + "</td>" +
//                 "<td>" + "<input " + "id=" + data[i].ID + "&UnitName" + " value='" + data[i].UnitName + "'>" + "</td>" +
//                 "<td>" + "<input " + "id=" + data[i].ID + "&CityName" + " value='" + data[i].CityName + "'>" + "</td>" +
//                 "<td>" + "<input " + "id=" + data[i].ID + "&StartDate" + " value=" + data[i].StartDate + ">" + "</td>" +
//                 "<td>" + "<input " + "id=" + data[i].ID + "&EndDate" + " value=" + data[i].EndDate + ">" + "</td>" +
//                 "<td>" + "<input " + "id=" + data[i].ID + "&Site" + " value=" + data[i].Site + ">" + "</td>" +
//                 "<td>" + "<input " + "id=" + data[i].ID + "&Exhibitor" + " value=" + data[i].Exhibitor + ">" + "</td>" +
//                 "<td>" + "<input " + "id=" + data[i].ID + "&Visitor" + " value=" + data[i].Visitor + ">" + "</td>" +
//                 "<td>" + "<input " + "id=" + data[i].ID + "&ExpoArea" + " value=" + data[i].ExpoArea + ">" + "</td>" +
//                 "<td>" + "<input " + "id=" + data[i].ID + "&GetDate" + " value=" + data[i].GetDate + ">" + "</td>" +
//                 "<td><a href='#' id=" + data[i].ID + ">" + 'del' + "</a></td>" +
//                 "</tr>");
//         }
//     }

//     //添加一行
//     function addRow() {
//         $('#event-info').append(
//             "<tr>" +
//             "<td></td>" +
//             "<td></td>" +
//             "<td><span>" + "<input " + "name=" + "addItemid" + " value=''" + ">" + "</span></td>" +
//             "<td><span>" + "<input " + "name=" + "addSid" + " value=''" + ">" + "</span></td>" +
//             "<td><span>" + "<input " + "name=" + "addExpoName" + " value=''" + ">" + "</span></td>" +
//             "<td><span>" + "<input " + "name=" + "addUnitCode" + " value=''" + ">" + "</span></td>" +
//             "<td><span>" + "<input " + "name=" + "addUnitName" + " value=''" + ">" + "</span></td>" +
//             "<td><span>" + "<input " + "name=" + "addCityName" + " value=''" + ">" + "</span></td>" +
//             "<td><span>" + "<input " + "name=" + "addStartDate" + " value=''" + ">" + "</span></td>" +
//             "<td><span>" + "<input " + "name=" + "addEndDate" + " value=''" + ">" + "</span></td>" +
//             "<td><span>" + "<input " + "name=" + "addSite" + " value=''" + ">" + "</span></td>" +
//             "<td><span>" + "<input " + "name=" + "addExhibitor" + " value=''" + ">" + "</span></td>" +
//             "<td><span>" + "<input " + "name=" + "addVisitor" + " value=''" + ">" + "</span></td>" +
//             "<td><span>" + "<input " + "name=" + "addExpoArea" + " value=''" + ">" + "</span></td>" +
//             "<td><span>" + "<input " + "name=" + "addGetDate" + " value=''" + ">" + "</span></td>" +
//             "<td><span><a href='#' id='addSure'" + ">" + 'add' + "</a></span></td>" +
//             "</tr>");
//     }

//     //拖动改变表格宽度
//     $(function() {
//         $("#events").colResizable({
//             liveDrag: true,
//             gripInnerHtml: "<div class='grip'></div>",
//             draggingClass: "dragging"
//         });
//     });

//     //初始化选择框
//     $(window).on('load', function() {
//         $('.selectpicker').selectpicker({
//             'selectedText': 'cat'
//         });
//     });

//     //把选中的列赋值给hidden_column输入框
//     $("#id_select").change(function() {
//         var column = $("#id_select").val();
//         select_column = column.toString().split(',');
//         $("#hidden_column").val(select_column);
//         showColumn();
//     });

//     //根据hidden_column输入框的值显示或隐藏列
//     function showColumn() {
//         var column = $("#hidden_column").val();
//         if (column != '') {
//             select_column = column.toString().split(',');
//             //alert(select_column);
//             $('table tr').find("th").show();
//             $('table tr').find("td").show();
//             $.each(select_column, function(n, value) {
//                 $('table tr').find("th:eq(" + value + ")").hide();
//                 $('table tr').find("td:eq(" + value + ")").hide();
//             });
//         }
//     }

// });