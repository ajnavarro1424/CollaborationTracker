  <!-- Ask Matt to look at this, its causing errors with passing classes to jinja objects  -->
  <!-- {% macro (field) %} -->
  <!-- <div class="form_field">
    {{ field.label }} {{ field(**kwargs)|safe }}
    {% if field.errors %}
    {% set css_class = 'has_error ' + kwargs.pop('class', '') %}
    {{ field(class=css_class, **kwargs) }}
    <ul class="errors">{% for error in field.errors %}<li>{{ error|e }}</li>{% endfor %}</ul>
    {% else %}
    {{ field(**kwargs) }}
    {% endif %}
  </div>
  {% endmacro %} -->

  <!-- {% macro make_label(field) %}
    <div class="form_field">on theleft{{ field.label }}:</div>
  {% endmacro %}
