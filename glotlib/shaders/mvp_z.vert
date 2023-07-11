#version 330

layout (location = 0) in vec2 a_vertex;
uniform mat4  u_mvp;
uniform float u_z;

void main()
{
    gl_Position = u_mvp * vec4(a_vertex, u_z, 1);
}
