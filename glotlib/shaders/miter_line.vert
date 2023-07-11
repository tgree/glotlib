// Based on: https://stackoverflow.com/q/60440682
#version 330

uniform samplerBuffer u_line_vertices;
uniform mat4  u_mvp;
uniform vec2  u_resolution;
uniform float u_width;
uniform float u_z;

void main()
{
    int line_i = gl_VertexID / 6;
    int tri_i  = gl_VertexID % 6;

    vec2 va[4];
    for (int i=0; i<4; ++i)
    {
        vec4 tex   = texelFetch(u_line_vertices, line_i + i);
        va[i]      = (u_mvp * tex).xy;
        va[i]      = (va[i] + 1.0) * 0.5 * u_resolution;
    }

    vec2 v_line  = normalize(va[2] - va[1]);
    vec2 nv_line = vec2(-v_line.y, v_line.x);

    vec2 pos;
    vec2 v_adjacent;
    float multiplier;
    if (tri_i == 0 || tri_i == 1 || tri_i == 3)
    {
        // Previous segment is the adjacent one.
        v_adjacent = normalize(va[1] - va[0]);
        pos        = va[1];
        multiplier = (tri_i == 1 ? -0.5 : 0.5);
    }
    else
    {
        // Next segment is the adjacent one.
        v_adjacent = normalize(va[3] - va[2]);
        pos        = va[2];
        multiplier = (tri_i == 5 ? 0.5 : -0.5);
    }
    vec2 v_miter = normalize(nv_line + vec2(-v_adjacent.y, v_adjacent.x));
    pos += v_miter * u_width * multiplier / dot(v_miter, nv_line);

    pos = pos / u_resolution * 2.0 - 1.0;
    gl_Position.xy = pos;
    gl_Position.zw = vec2(u_z, 1);
}
