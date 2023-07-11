#version 330

uniform vec4 u_color;
uniform sampler2D u_sampler;

in vec2 texcoord;
out vec4 fragColor;

void main()
{
    vec2 tc   = vec2(texcoord.x, texcoord.y);
    fragColor = vec4(0, 0, 0, texture(u_sampler, tc).r);
    //fragColor = vec4(0, 0, 0, 1);
}
