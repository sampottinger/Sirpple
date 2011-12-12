{{name}} = function({{ args }})
{
    {% autoescape off %}{{body}}{% endautoescape %}
};
