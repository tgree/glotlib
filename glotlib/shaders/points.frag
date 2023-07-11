#version 330

uniform vec4 u_color;

out vec4 fragColor;

void main()
{
    vec2 coord = gl_PointCoord - vec2(0.5);
    if (dot(coord, coord) > 0.25)
        discard;

    fragColor = u_color;
}
