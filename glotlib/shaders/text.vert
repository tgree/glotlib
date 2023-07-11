#version 330

layout (location = 0) in vec2 a_vertex;
layout (location = 1) in vec2 a_texcoord;

uniform mat4  u_mvp;
uniform float u_z;

out vec2 texcoord;

void main()
{
    gl_Position = u_mvp * vec4(a_vertex, u_z, 1);
    texcoord = a_texcoord;
}
